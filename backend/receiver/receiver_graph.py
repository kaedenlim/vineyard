import os
import requests
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
from typing import Optional
from threading import Thread
import time
from datetime import datetime, timedelta, timezone
import pika
import json
from fastapi import Request, Response
from fastapi import APIRouter
import logging


load_dotenv()

# Config
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
EMAIL_USER = os.getenv("EMAIL_ADDRESS")
PROCESSOR_URL = os.getenv("PROCESSOR_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# CLIENT_STATE = os.getenv("CLIENT_STATE")
CLIENT_STATE = "secure123"


GRAPH_TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

app = FastAPI()
logger = logging.getLogger(__name__)
subscription_id = None  # Store globally for renewal

# ✅ Track message IDs that were already handled
processed_messages = set()

def get_expiration_datetime():
    max_expiration = datetime.now(timezone.utc) + timedelta(minutes=10060)
    return max_expiration.isoformat(timespec='seconds').replace('+00:00', 'Z')

def get_access_token():
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    res = requests.post(GRAPH_TOKEN_URL, data=data)
    try:
        res.raise_for_status()
    except requests.HTTPError:
        print("❌ Token request failed:", res.text)
        raise
    return res.json()["access_token"]

def create_subscription():
    global subscription_id
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "changeType": "created",
        "notificationUrl": WEBHOOK_URL,
        "resource": f"/users/{EMAIL_USER}/mailFolders('Inbox')/messages",
        "expirationDateTime": get_expiration_datetime(),
        "clientState": CLIENT_STATE
    }
    res = requests.post(f"{GRAPH_API_BASE}/subscriptions", headers=headers, json=payload)
    if res.status_code == 201:
        subscription_id = res.json()["id"]
        print(f"✅ Subscription created: {subscription_id}")
    else:
        print(f"❌ Subscription creation failed: {res.status_code} - {res.text}")

def renew_subscription():
    global subscription_id
    while True:
        time.sleep(60 * 60)  # Every hour
        if not subscription_id:
            print("⏳ Subscription ID not set. Attempting to create...")
            create_subscription()
            continue

        try:
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            new_expiry = get_expiration_datetime()
            res = requests.patch(
                f"{GRAPH_API_BASE}/subscriptions/{subscription_id}",
                headers=headers,
                json={"expirationDateTime": new_expiry}
            )
            if res.status_code == 200:
                print(f"🔄 Subscription {subscription_id} renewed.")
            else:
                print(f"⚠️ Failed to renew subscription: {res.status_code} - {res.text}")
                subscription_id = None  # Force re-create next cycle
        except Exception as e:
            print(f"❌ Error renewing subscription: {e}")
            subscription_id = None
            
            
def mark_as_read(message_id):
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    patch_url = f"{GRAPH_API_BASE}/users/{EMAIL_USER}/messages/{message_id}"
    patch_body = {"isRead": True}
    
    res = requests.patch(patch_url, headers=headers, json=patch_body)
    if res.status_code == 200:
        print(f"📩 Marked message {message_id} as read.")
    else:
        print(f"❌ Failed to mark as read: {res.status_code} - {res.text}")
            
def fetch_email_details(message_id):
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_API_BASE}/users/{EMAIL_USER}/messages/{message_id}"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    msg = res.json()
    
    # ✅ Skip if message is already read
    if msg.get("isRead", False):
        print(f"👀 Skipping already-read message: {msg.get('id')}")
        return None

    return {
        "email_text": msg.get("body", {}).get("content", ""),
        "sender": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
        "subject": msg.get("subject", ""),
        "conversation_id": msg.get("conversationId", ""),
        "message_id": msg.get("id")
    }

def forward_to_processor(email_data: dict, retries: int = 3):
    for attempt in range(retries):
        try:
            res = requests.post(PROCESSOR_URL, json=email_data, timeout=30)
            if res.ok:
                print("✅ Forwarded to process_email_comp")
                final_reply = res.json()
                final_reply['sender'] = email_data.get('sender')
                final_reply['subject'] = email_data.get('subject')
                final_reply['message_id'] = email_data.get('message_id')
                print("📦 Final reply to send:", final_reply)
                publish_to_sender_queue(final_reply)
                return
            else:
                print(f"⚠️ Attempt {attempt+1}: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"❌ Attempt {attempt+1} failed: {e}")
        time.sleep(2)
        
def publish_to_sender_queue(email_payload: dict):
    
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "rabbitmq"))
        )
        channel = connection.channel()
        channel.queue_declare(queue="send_email_queue", durable=True)

        channel.basic_publish(
            exchange='',
            routing_key='send_email_queue',
            body=json.dumps(email_payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print("📨 Sent email to sender_graph.py via RabbitMQ")
        connection.close()
    except Exception as e:
        print(f"❌ Failed to publish to sender queue: {e}")
        
        
@app.get("/notifications")
async def verify_subscription(request: Request):
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return Response(content=validation_token, media_type="text/plain")
    return {"error": "No validation token found"}

@app.post("/notifications")
async def receive_notification(request: Request):
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return Response(content=validation_token, media_type="text/plain")

    body = await request.json()
    for notification in body.get("value", []):
        if notification.get("clientState") != CLIENT_STATE:
            print("⚠️ Invalid client state. Skipping.")
            continue
        message_id = notification.get("resourceData", {}).get("id")
        if message_id:
            if message_id in processed_messages:
                print(f"🔁 Duplicate message {message_id} skipped.")
                continue

            processed_messages.add(message_id)
            try:
                email_data = fetch_email_details(message_id)
                mark_as_read(message_id)
                
                # ✅ Skip if email was already read
                if not email_data:
                    print(f"📭 No email data returned. Skipping.")
                    continue
                
                print(f"📬 Email data to send: {email_data}")

                # --- NEW FILTER: skip emails sent by our own AI user ---
                if email_data.get("sender", "").lower() == EMAIL_USER.lower():
                    print("⏭️ Skipping email sent by own system to prevent loops.")
                    continue

                forward_to_processor(email_data)
            except Exception as e:
                print(f"❌ Error handling message: {e}")

    return {"status": "received"}


    
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Startup event fired!")
    print("🚀 Startup event fired!")  # Also print to stdout
    Thread(target=create_subscription).start()
    Thread(target=renew_subscription, daemon=True).start()

# if __name__ == "__main__":
#     uvicorn.run("receiver_graph:app", host="0.0.0.0", port=8005, reload=True)