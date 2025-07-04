from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import re
import pika
import json
import time

logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()

def connect_to_rabbitmq(url: str, retries: int = 10, delay: int = 5):
    for attempt in range(retries):
        try:
            params = pika.URLParameters(url)
            connection = pika.BlockingConnection(params)
            logger.info("✅ Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"🐇 RabbitMQ not ready. Retry {attempt + 1}/{retries} in {delay}s... Error: {e}")
            time.sleep(delay)
    raise Exception("❌ Failed to connect to RabbitMQ after multiple retries")

def generate_regulatory_guidance(product_type: str, market_info: str, language: str) -> str:
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
                {"role": "system", "content": "You are a regulatory and legal expert specializing in ecommerce. Write a very concise summary of key regulatory and legal considerations relevant to the given product type and user-supplied knowledge about the market. Focus on compliance requirements, potential legal risks, necessary certifications or licenses, and any jurisdiction-specific regulations. Keep your guidance actionable and practical, suitable for a founder preparing to enter the market. Your output should be in the language indicated."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Error generating regulatory guidance: {str(e)}")
        return f"Error generating regulatory guidance: {str(e)}"

def on_request(ch, method, props, body):
    logger.info(f"Received message: {body.decode('utf-8')}")
    try:
        data = json.loads(body)
        product_type = data.get("product_type", "")
        market_info = data.get("market_info", "")
        language = data.get("language", "")
    except Exception as e:
        logger.warning(f"Error parsing message body: {str(e)}")
        product_type = ""
        market_info = ""
        language = ""

    if product_type == "test":
        response = "test"
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Sent response: {response}")
        return

    research_text = generate_regulatory_guidance(product_type, market_info, language)
    logger.info("Successfully generated market research insights")

    # Clean Markdown code block if present
    cleaned_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", research_text.strip(), flags=re.MULTILINE)

    response = cleaned_text

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
    connection = connect_to_rabbitmq(rabbitmq_url)
    channel = connection.channel()

    channel.queue_declare(queue='regulatory_queue', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='regulatory_queue', on_message_callback=on_request)

    logger.info("Awaiting RPC requests on 'regulatory_queue'")
    channel.start_consuming()

if __name__ == "__main__":
    main()