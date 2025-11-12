import json
import os
import requests

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
QUOTE_API = "https://api.animechan.io/v1/quotes/random"
RICKROLL_GIF = "https://media.giphy.com/media/Vuw9m5wXviFIQ/giphy.gif" 


# --- Poll messages from Telegram ---
def poll_messages():
    """Poll recent updates from Telegram."""
    response = requests.get(f"{TELEGRAM_API}/getUpdates")
    return response.json()


# --- Send text message ---
def send_message(chat_id, text):
    """Send text message to a Telegram chat."""
    payload = {"chat_id": chat_id, "text": text}
    return requests.post(f"{TELEGRAM_API}/sendMessage", json=payload).json()


# --- Send animation (GIF) ---
def send_gif(chat_id, gif_url):
    """Send a GIF to the chat."""
    payload = {"chat_id": chat_id, "animation": gif_url}
    return requests.post(f"{TELEGRAM_API}/sendAnimation", json=payload).json()


# --- Quote generator logic ---
def get_random_quote():
    """Fetch random anime quote from API."""
    try:
        r = requests.get(QUOTE_API)
        data = r.json()
        quote = data["data"]["content"]
        anime_name = data["data"]["anime"]["name"]
        who_said_it = data["data"]["character"]["name"]
        return f"\"{quote}\"\n- {who_said_it} ({anime_name})"
    except Exception:
        return "⚠️ Could not fetch a quote right now."


# --- Handle incoming Telegram message ---
def handle_message(text, chat_id):
    """Respond to commands."""
    text = text.strip().lower()

    if text.startswith("/hello"):
        return send_message(chat_id, "👋 Hey there!")

    elif text.startswith("/help"):
        msg = (
            "Here are my commands:\n"
            "/hello - Say hi\n"
            "/echo <text> - I’ll repeat your text\n"
            "/q - Get a random anime quote\n"
            "/roll - roll for a suprise\n"
            "/help - Show this help message"
        )
        return send_message(chat_id, msg)

    elif text.startswith("/echo"):
        parts = text.split(" ", 1)
        if len(parts) > 1:
            return send_message(chat_id, f"🗣️ {parts[1]}")
        else:
            return send_message(chat_id, "Usage: /echo <text>")

    elif text.startswith("/q"):
        quote_text = get_random_quote()
        return send_message(chat_id, quote_text)

    elif text.startswith("/roll") or text == "roll":
        send_message(chat_id, "🎵 Never gonna give you up... 🎶")
        return send_gif(chat_id, RICKROLL_GIF)

    else:
        return send_message(chat_id, "❓ Unknown command. Try /help")


# --- Main Lambda handler ---
def lambda_handler(event, context):
    """
    Main Lambda handler.
    - Manually invoke this using awslocal lambda invoke
    - It polls Telegram messages and responds accordingly
    """
    try:
        result = poll_messages()

        if not result.get("ok"):
            return {"statusCode": 400, "body": "Telegram API error"}

        updates = result.get("result", [])
        if not updates:
            return {"statusCode": 200, "body": "No messages"}

        # Process the last message only
        last_update = updates[-1]
        message = last_update.get("message")
        if not message:
            return {"statusCode": 200, "body": "Not a message"}

        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        handle_message(text, chat_id)

        return {"statusCode": 200, "body": json.dumps({"message": text})}

    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
