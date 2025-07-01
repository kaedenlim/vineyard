from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import pika
import json
import re

logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()

def generate_market_research(product_type: str, market_info: str, language: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    client = OpenAI(api_key=api_key)

    prompt = f"""
    Product Type: {product_type}
    Market Info: {market_info}
    Language: {language}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an ecommerce market research expert. Write a very concise summary of market insights relevant to the given product type and user-supplied knowledge about the market. Focus on market trends, key customer segments, major competitors (including actual brands), and potential opportunities or risks. Keep your response actionable and practical, suitable for a founder preparing to enter the given market. Your output should be in the language indicated."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Error generating market research: {str(e)}")
        return f"Error generating market research: {str(e)}"

def on_request(ch, method, props, body):
    logger.info(f"Received message: {body.decode('utf-8')}")
    try:
        data = json.loads(body)
        product_type = data.get("product_type", "")
        market_info = data.get("market_info", "")
        language = data.get("language", "")

        if product_type == "test":
            response = "test"
            ch.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id = props.correlation_id),
                body=response
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Sent response: {response}")
            return

        research_text = generate_market_research(product_type, market_info, language)
        logger.info("Successfully generated market research insights")

        # Clean Markdown code block if present
        cleaned_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", research_text.strip(), flags=re.MULTILINE)

        response = cleaned_text
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        response = f"Error processing request: {str(e)}"

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id = props.correlation_id),
        body=response
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)
    logger.info(f"Sent response: {response}")

def main():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    params = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='general_queue', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='general_queue', on_message_callback=on_request)

    logger.info("Awaiting RPC requests on 'general_queue'")
    channel.start_consuming()

if __name__ == "__main__":
    main()