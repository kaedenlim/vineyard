import os
import json
import pika
import requests
from dotenv import load_dotenv
import time

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
EMAIL_USER = os.getenv("EMAIL_ADDRESS")

GRAPH_TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

def get_access_token():
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    res = requests.post(GRAPH_TOKEN_URL, data=data)
    res.raise_for_status()
    return res.json()["access_token"]

def format_reply_html(data: dict) -> str:
    html = "<h2>AI Response</h2>"
    for key, value in data.items():
        section_title = key.replace("_", " ").title()
        html += f"<h3>{section_title}</h3><p>{value}</p>"
    return html

def send_email(to_email, subject, body, in_reply_to=None):
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    if in_reply_to:
        # 1. Create reply draft
        reply_draft_res = requests.post(
            f"{GRAPH_API_BASE}/users/{EMAIL_USER}/messages/{in_reply_to}/createReply",
            headers=headers
        )

        if reply_draft_res.status_code != 201:
            print(f"❌ Failed to create reply draft: {reply_draft_res.status_code} - {reply_draft_res.text}")
            return False
        

        reply_draft = reply_draft_res.json()
        reply_id = reply_draft["id"]

        # 2. Update draft with ONLY the 'body' property (fix for ErrorIncorrectUpdatePropertyCount)
        patch_body = {
        "body": {
            "contentType": "HTML",
            "content": body
        }
        }

        patch_res = requests.patch(
            f"{GRAPH_API_BASE}/users/{EMAIL_USER}/messages/{reply_id}",
            headers=headers,
            json=patch_body
        )

        if patch_res.status_code != 200:
            print(f"❌ Failed to update reply draft: {patch_res.status_code} - {patch_res.text}")
            return False

        # 3. Send the reply draft
        send_res = requests.post(
            f"{GRAPH_API_BASE}/users/{EMAIL_USER}/messages/{reply_id}/send",
            headers=headers
        )

        if send_res.status_code == 202:
            print(f"✅ Reply sent to {to_email}")
            return True
        else:
            print(f"❌ Failed to send reply: {send_res.status_code} - {send_res.text}")
            return False

    # Fallback: send a new email (non-threaded)
    email_payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": to_email}}
            ]
        },
        "saveToSentItems": "true"
    }

    res = requests.post(f"{GRAPH_API_BASE}/users/{EMAIL_USER}/sendMail", headers=headers, json=email_payload)

    if res.status_code == 202:
        print(f"✅ Email sent to {to_email}")
        return True
    else:
        print(f"❌ Failed to send email: {res.status_code} - {res.text}")
        return False

def callback(ch, method, properties, body):
    print("📨 Received message from queue")
    data = json.loads(body)
    
    to_email = data.get("sender")
    subject = data.get("subject")
    message_id = data.get("message_id")

    # Build formatted response
    general = data.get("general_insights", "")
    regulatory = data.get("regulatory_insights", "")
    quantitative = data.get("quantitative_insights", "")

    response = (
        f"<p><strong>General Insights:</strong><br>{general}</p>"
        f"<p><strong>Regulatory Insights:</strong><br>{regulatory}</p>"
        f"<p><strong>Quantitative Insights:</strong><br>{quantitative}</p>"
    )
    
    print("✉️ Sending email with:")
    print("To:", to_email)
    print("Subject:", subject)
    print("Body:", response)

    success = send_email(to_email, subject, response, in_reply_to=message_id)

    if success:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print("⚠️ Email failed. Message will be retried.")

def connect_to_rabbitmq(host='rabbitmq', retries=10, delay=5):
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            print("✅ Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"⏳ RabbitMQ not ready, retry {i+1}/{retries} in {delay}s...")
            time.sleep(delay)
    raise Exception("❌ Failed to connect to RabbitMQ after multiple retries")

def consume():
    connection = connect_to_rabbitmq(host='rabbitmq')
    channel = connection.channel()
    channel.queue_declare(queue='send_email_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='send_email_queue', on_message_callback=callback)
    print("🔁 Waiting for messages to send replies...")
    channel.start_consuming()

print("🚀 Starting sender_graph...")
consume()