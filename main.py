import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = "soapai_verify_token"  # You choose this (we'll use it in Meta)

# 🔹 Webhook verification (Meta uses this)
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "Verification failed"}


# 🔹 Receive incoming messages
@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    print("Incoming message:", body)

    try:
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        text = message["text"]["body"]

        send_message(sender, f"🧼 SoapAI received: {text}")

    except Exception as e:
        print("Error processing message:", e)

    return {"status": "ok"}


def send_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("Send response:", response.status_code, response.text)