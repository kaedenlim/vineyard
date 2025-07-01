from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn
import os
import logging
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import json
import re
import pika
import uuid
import threading
import asyncio

def send_task_with_callback(queue_name, message_body, reply_to_queue):
    """
    Sends a message to a RabbitMQ queue with a unique correlation_id and reply_to queue.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_declare(queue=reply_to_queue, durable=True)
    correlation_id = str(uuid.uuid4())
    future = loop.create_future()
    pending_results[correlation_id] = future
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message_body),
        properties=pika.BasicProperties(
            reply_to=reply_to_queue,
            correlation_id=correlation_id,
            content_type='application/json'
        )
    )
    connection.close()
    return correlation_id, future

logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI()

load_dotenv()

class ProcessEmailRequest(BaseModel):
    email_text: str

def parse_email(raw_text) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    client = OpenAI(api_key=api_key)

    prompt = f"""
    Parse the following email and extract the relevant information.

    {raw_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are an ecommerce market entry expert. You analyze informal emails from entrepreneurs and return structured insights. Output a JSON object with the following fields:
                1. 'product_type': a short but specific name or category of the product (e.g., 'natural skincare', 'wireless earbuds', 'organic pet food').
                2. 'scrape_client': set to true if the sender explicitly requires reference to their own products/storepage, otherwise false.
                3. 'market_info': a summary of what the sender knows or assumes about the market and what aspects they want to explore further.
                4. 'language': the language in which the original input is written in.
                If the email contains no clear information, set all fields to 'test'."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Error parsing email: {str(e)}")
        return f"Error parsing email: {str(e)}"

# In-memory dictionary to track pending results keyed by correlation_id
pending_results = {}
loop = asyncio.get_event_loop()

def callback_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    callback_queue = 'email_processor_callback_queue'
    channel.queue_declare(queue=callback_queue, durable=True)

    def on_message(ch, method, properties, body):
        correlation_id = properties.correlation_id
        logger.info(f"Received message with correlation_id: {correlation_id}")
        if correlation_id and correlation_id in pending_results:
            result = body.decode()
            # Set the result in the future
            future = pending_results.pop(correlation_id)
            loop.call_soon_threadsafe(future.set_result, result)
        else:
            logger.warning(f"Received unmatched correlation_id: {correlation_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=callback_queue, on_message_callback=on_message)
    channel.start_consuming()

@app.on_event("startup")
def startup_event():
    threading.Thread(target=callback_listener, daemon=True).start()

@app.post("/process_email")
async def interpret_data(data: ProcessEmailRequest):
    logger.info("Endpoint /process_email hit")
    raw_text = data.email_text
    
    parsed_text = parse_email(raw_text)
    logger.info(f"Successfully parsed email: {parsed_text}")

    # Clean Markdown code block if present
    cleaned_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", parsed_text.strip(), flags=re.MULTILINE)

    try:
        parsed_json = json.loads(cleaned_text)
        # Send tasks to RabbitMQ queues instead of calling services directly
        reply_to_queue = "email_processor_callback_queue"
        general_correlation_id, general_future = send_task_with_callback("general_queue", parsed_json, reply_to_queue)
        logger.info(f"Task sent to general_queue with correlation_id: {general_correlation_id}")
        regulatory_correlation_id, regulatory_future = send_task_with_callback("regulatory_queue", parsed_json, reply_to_queue)
        logger.info(f"Task sent to regulatory_queue with correlation_id: {regulatory_correlation_id}")
        quantitative_correlation_id, quantitative_future = send_task_with_callback("quantitative_queue", parsed_json, reply_to_queue)
        logger.info(f"Task sent to quantitative_queue with correlation_id: {quantitative_correlation_id}")

        try:
            general_result, regulatory_result, quantitative_result = await asyncio.wait_for(
                asyncio.gather(general_future, regulatory_future, quantitative_future),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for results from queues")
            # Remove pending futures to prevent memory leaks
            pending_results.pop(general_correlation_id, None)
            pending_results.pop(regulatory_correlation_id, None)
            pending_results.pop(quantitative_correlation_id, None)
            return JSONResponse(content={"error": "Timeout waiting for results from queues"}, status_code=504)

        return JSONResponse(content={
            "general_insights": general_result,
            "regulatory_insights": regulatory_result,
            "quantitative_insights": quantitative_result
        })
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Failed to parse GPT response as JSON", "raw_response": parsed_text}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("process_email_comp:app", host="0.0.0.0", port=8006, reload=True)