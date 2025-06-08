import asyncio
import json
import logging
import os
import uuid

import httpx
import pika

logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def scrape_client_data(client: httpx.AsyncClient, product_type: str) -> dict:
    logger.info(f"Scraping client for product: {product_type}")
    client_request_body = {
        "lazada_url": f"https://dummy.lazada.com/{product_type}",
        "carousell_url": f"https://dummy.carousell.com/{product_type}"
    }
    try:
        response = await client.post("http://localhost:8003/scrape/client", json=client_request_body)
        response_json = response.json()
        logger.info(f"Client scrape succeeded for product: {product_type}")
        return {"results": response_json}
    except httpx.RequestError as e:
        logger.error(f"Client scrape service unavailable: {str(e)}")
        return {"error": f"Client scrape service unavailable: {str(e)}"}
    except ValueError as e:
        logger.error(f"Invalid JSON from scrape client: {str(e)}")
        return {"error": f"Invalid JSON from scrape client: {str(e)}"}

async def scrape_market_data(client: httpx.AsyncClient, product_type: str) -> dict:
    logger.info(f"Scraping market for product: {product_type}")
    product_request_body = {
        "product": product_type
    }
    try:
        response = await client.post("http://localhost:8003/scrape/markets", json=product_request_body)
        response_json = response.json()
        logger.info(f"Market scrape succeeded for product: {product_type}")
        return {"results": response_json}
    except httpx.RequestError as e:
        logger.error(f"Product scrape service unavailable: {str(e)}")
        return {"error": f"Product scrape service unavailable: {str(e)}"}
    except ValueError as e:
        logger.error(f"Invalid JSON from scrape product: {str(e)}")
        return {"error": f"Invalid JSON from scrape product: {str(e)}"}

def format_for_interpretation(data):
    if not data or "scraped_data" not in data:
        return {}
    top_items = sorted(data["scraped_data"], key=lambda x: x.get("Ranking", float("inf")))[:2]
    return {
        "top_listings": top_items,
        "average_price": data.get("average_price")
    }

async def interpret_data(client: httpx.AsyncClient, product_type: str, results: dict) -> dict:
    logger.info(f"Interpreting data for product: {product_type}")

    interpret_request_body = {
        "product": product_type,
        "lazada_results": format_for_interpretation(results.get("lazada")),
        "carousell_results": format_for_interpretation(results.get("carousell"))
    }
    try:
        response = await client.post("http://localhost:8004/interpret_data", json=interpret_request_body)
        response_json = response.json()
        logger.info(f"Interpretation succeeded for product: {product_type}")
        return response_json
    except httpx.RequestError as e:
        logger.error(f"Interpretation service unavailable: {str(e)}")
        return {"error": f"Interpretation service unavailable: {str(e)}"}
    except ValueError as e:
        logger.error(f"Invalid JSON from interpretation service: {str(e)}")
        return {"error": f"Invalid JSON from interpretation service: {str(e)}"}

async def process_message(body: bytes):
    try:
        data = json.loads(body)
        product_type = data.get("product_type", "")
        scrape_client = data.get("scrape_client", False)
    except Exception as e:
        logger.error(f"Invalid message format: {str(e)}")
        return {"error": f"Invalid message format: {str(e)}"}

    if product_type == "test":
        return "test"

    logger.info(f"Starting quantitative analysis: product_type={product_type}, scrape_client={scrape_client}")
    final_response = {}

    async with httpx.AsyncClient(timeout=30) as client:
        scrape_tasks = []
        if scrape_client:
            scrape_tasks.append(scrape_client_data(client, product_type))
        scrape_tasks.append(scrape_market_data(client, product_type))

        scrape_results = await asyncio.gather(*scrape_tasks)

        if scrape_client:
            client_result = scrape_results[0]
            market_result = scrape_results[1]
        else:
            client_result = None
            market_result = scrape_results[0]

        if client_result:
            if "results" in client_result:
                final_response["client_scrape_results"] = client_result["results"]
            if "error" in client_result:
                final_response["client_error"] = client_result["error"]

        if "results" in market_result:
            final_response["market_scrape_results"] = market_result["results"]
        if "error" in market_result:
            final_response["market_error"] = market_result["error"]

        # Combine results for interpretation
        combined_results = {}
        if "client_scrape_results" in final_response:
            combined_results.update(final_response["client_scrape_results"])
        if "market_scrape_results" in final_response:
            combined_results.update(final_response["market_scrape_results"])

        # Interpret combined results
        interpretation = await interpret_data(client, product_type, combined_results)
        final_response["interpretation"] = interpretation

    # Handle total failure
    if scrape_client and final_response.get("client_error") and final_response.get("market_error"):
        return {
            "client_error": final_response["client_error"],
            "market_error": final_response["market_error"]
        }

    # Ensure streamlit_data directory exists
    os.makedirs("streamlit_data", exist_ok=True)

    # Generate a unique token
    token = str(uuid.uuid4())
    streamlit_path = os.path.join("streamlit_data", f"{token}.json")

    # Save relevant data to file
    with open(streamlit_path, "w") as f:
        json.dump({
            "product": product_type,
            "market_scrape_results": final_response.get("market_scrape_results"),
            "client_scrape_results": final_response.get("client_scrape_results"),
            "interpretation": final_response.get("interpretation")
        }, f, indent=2)

    # Include token in final response
    final_response["token"] = token

    # Generate streamlit_url
    streamlit_url = f"https://nikolauappio-mfgcensvkzpmqdygjnqksv.streamlit.app.com?token={token}"
    return streamlit_url

def main():
    connection_params = pika.ConnectionParameters(host='rabbitmq')
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue='quantitative_queue', durable=True)
    
    def on_request(ch, method, props, body):
        logger.info(f"Received message: {body.decode('utf-8')}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(process_message(body))
        loop.close()

        if isinstance(response, str):
            response_body = response
        else:
            response_body = json.dumps(response)

        logger.info(f"Sent response: {response_body}")
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response_body
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='quantitative_queue', on_message_callback=on_request)

    logger.info("Awaiting RPC requests on 'quantitative_queue'")
    channel.start_consuming()

if __name__ == "__main__":
    main()
