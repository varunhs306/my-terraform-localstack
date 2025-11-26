import json
import os
import logging
import boto3
import requests
from datetime import datetime, timezone
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Telegram setup
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("DDB_TABLE_NAME", "my-ls-table1")
table = dynamodb.Table(TABLE_NAME)


def poll_messages():
    """Poll Telegram API for new messages."""
    logger.info("Polling for new messages from Telegram API")
    try:
        url = f"{TELEGRAM_API}/getUpdates"
        params = {
            "timeout": 30,
            "offset": -1  # Get only the last update
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Poll response: {json.dumps(result)}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Error polling Telegram API: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}


def send_message(chat_id, text):
    """Send a message to a Telegram chat."""
    logger.info(f"Sending message to chat_id={chat_id}: {text[:50]}...")
    try:
        url = f"{TELEGRAM_API}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Message sent successfully to chat_id={chat_id}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to chat_id={chat_id}: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}


def save_user_data(user_id, username, data):
    """Save user data to DynamoDB."""
    logger.info(f"Saving data for user_id={user_id}, username={username}")
    try:
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)  # milliseconds
        item = {
            "user_id": str(user_id),
            "timestamp": timestamp,
            "username": username or "unknown",
            "data": data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        table.put_item(Item=item)
        logger.info(f"Data saved successfully for user_id={user_id}, timestamp={timestamp}")
        return True
    except Exception as e:
        logger.error(f"Error saving data for user_id={user_id}: {str(e)}", exc_info=True)
        return False


def get_user_data(user_id):
    """Retrieve all data for a specific user from DynamoDB."""
    logger.info(f"Retrieving data for user_id={user_id}")
    try:
        response = table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": str(user_id)},
        )
        
        items = response.get("Items", [])
        logger.info(f"Retrieved {len(items)} items for user_id={user_id}")
        return items
    except Exception as e:
        logger.error(f"Error retrieving data for user_id={user_id}: {str(e)}", exc_info=True)
        return []


def delete_user_data(user_id, timestamp):
    """Delete a specific data entry for a user."""
    logger.info(f"Deleting data for user_id={user_id}, timestamp={timestamp}")
    try:
        table.delete_item(
            Key={
                "user_id": str(user_id),
                "timestamp": int(timestamp)
            }
        )
        logger.info(f"Data deleted successfully for user_id={user_id}, timestamp={timestamp}")
        return True
    except Exception as e:
        logger.error(f"Error deleting data for user_id={user_id}: {str(e)}", exc_info=True)
        return False


def handle_start_command(chat_id, username):
    """Handle /start command."""
    logger.info(f"Handling /start command for chat_id={chat_id}, username={username}")
    welcome_message = f"""
👋 *Welcome to the Data Storage Bot!*

Hello @{username}! I can help you store and retrieve your personal data.

*Available Commands:*
📝 `/save <your data>` - Save new data
📋 `/list` - View all your saved data
🗑️ `/delete <number>` - Delete a specific entry
❓ `/help` - Show this help message

*Example:*
`/save My important note`
`/list`
`/delete 1`

Your data is private and isolated from other users! 🔒
    """
    send_message(chat_id, welcome_message)


def handle_save_command(chat_id, user_id, username, data):
    """Handle /save command."""
    logger.info(f"Handling /save command for user_id={user_id}, data length={len(data)}")
    
    if not data or data.strip() == "":
        logger.warning(f"Empty data provided by user_id={user_id}")
        send_message(chat_id, "❌ Please provide some data to save!\n\nUsage: `/save your data here`")
        return
    
    success = save_user_data(user_id, username, data.strip())
    
    if success:
        logger.info(f"Data saved successfully for user_id={user_id}")
        send_message(chat_id, f"✅ Data saved successfully!\n\n📝 *Your data:*\n`{data.strip()}`")
    else:
        logger.error(f"Failed to save data for user_id={user_id}")
        send_message(chat_id, "❌ Failed to save data. Please try again later.")


def handle_list_command(chat_id, user_id):
    """Handle /list command."""
    logger.info(f"Handling /list command for user_id={user_id}")
    
    items = get_user_data(user_id)
    
    if not items:
        logger.info(f"No data found for user_id={user_id}")
        send_message(chat_id, "📭 You don't have any saved data yet.\n\nUse `/save <data>` to store something!")
        return
    
    # Sort by timestamp (newest first)
    items.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    message = f"📋 *Your Saved Data ({len(items)} items):*\n\n"
    
    for idx, item in enumerate(items, 1):
        timestamp = item.get("timestamp", 0)
        data = item.get("data", "")
        created_at = item.get("created_at", "")

        # Format timestamp for display
        try:
            # Convert Decimal to int (DynamoDB returns Decimal type)
            timestamp_value = int(timestamp) if timestamp else 0
            dt = datetime.fromtimestamp(timestamp_value / 1000)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            logger.warning(f"Failed to parse timestamp {timestamp}: {str(e)}")
            # Fallback to created_at if available
            try:
                if created_at:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    date_str = "Unknown date"
            except:
                date_str = "Unknown date"
        
        message += f"`{idx}.` *{date_str}*\n"
        message += f"   {data[:100]}{'...' if len(data) > 100 else ''}\n\n"
    
    message += f"\n💡 Use `/delete <number>` to remove an entry"
    
    logger.info(f"Sending {len(items)} items to user_id={user_id}")
    send_message(chat_id, message)


def handle_delete_command(chat_id, user_id, index_str):
    """Handle /delete command."""
    logger.info(f"Handling /delete command for user_id={user_id}, index={index_str}")
    
    if not index_str or not index_str.strip().isdigit():
        logger.warning(f"Invalid index provided by user_id={user_id}: {index_str}")
        send_message(chat_id, "❌ Please provide a valid number!\n\nUsage: `/delete <number>`\n\nUse `/list` to see your data with numbers.")
        return
    
    index = int(index_str.strip())
    
    # Get user's data
    items = get_user_data(user_id)
    
    if not items:
        logger.info(f"No data to delete for user_id={user_id}")
        send_message(chat_id, "📭 You don't have any saved data to delete.")
        return
    
    # Sort by timestamp (newest first) to match /list order
    items.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    if index < 1 or index > len(items):
        logger.warning(f"Index out of range for user_id={user_id}: {index}")
        send_message(chat_id, f"❌ Invalid number! Please choose between 1 and {len(items)}.\n\nUse `/list` to see your data.")
        return
    
    # Get the item to delete (index-1 because list is 0-indexed)
    item_to_delete = items[index - 1]
    timestamp = item_to_delete.get("timestamp")
    data = item_to_delete.get("data", "")
    
    success = delete_user_data(user_id, timestamp)
    
    if success:
        logger.info(f"Data deleted successfully for user_id={user_id}, index={index}")
        send_message(chat_id, f"✅ Data deleted successfully!\n\n🗑️ *Deleted:*\n`{data[:100]}`")
    else:
        logger.error(f"Failed to delete data for user_id={user_id}, index={index}")
        send_message(chat_id, "❌ Failed to delete data. Please try again later.")


def handle_message(text, chat_id, user_id, username):
    """Route messages to appropriate handlers based on command."""
    logger.info(f"Handling message from user_id={user_id}, chat_id={chat_id}, username={username}, text={text[:50]}")
    
    # Extract command and arguments
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    logger.info(f"Parsed command={command}, args_length={len(args)}")
    
    # Route to appropriate handler
    if command == "/start" or command == "/help":
        handle_start_command(chat_id, username)
    elif command == "/save":
        handle_save_command(chat_id, user_id, username, args)
    elif command == "/list":
        handle_list_command(chat_id, user_id)
    elif command == "/delete":
        handle_delete_command(chat_id, user_id, args)
    else:
        logger.info(f"Unknown command from user_id={user_id}: {command}")
        send_message(chat_id, f"❓ Unknown command: `{command}`\n\nUse `/help` to see available commands.")


def lambda_handler(event, context):
    """Main Lambda handler."""
    logger.info("=" * 80)
    logger.info("Lambda function invoked")
    logger.info(f"Event: {json.dumps(event)}")
    logger.info(f"Context: {context}")
    logger.info("=" * 80)
    
    try:
        # Validate environment variables
        if not TELEGRAM_TOKEN:
            logger.error("BOT_TOKEN environment variable not set")
            return {"statusCode": 500, "body": json.dumps({"error": "BOT_TOKEN not configured"})}
        
        logger.info(f"Using DynamoDB table: {TABLE_NAME}")
        logger.info(f"DynamoDB endpoint: {os.environ.get('DYNAMODB_ENDPOINT', 'default')}")
        
        # Poll for messages
        result = poll_messages()
        
        if not result.get("ok"):
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Telegram API returned error: {error_msg}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Telegram API error", "details": error_msg})
            }
        
        updates = result.get("result", [])
        logger.info(f"Received {len(updates)} updates")
        
        if not updates:
            logger.info("No new messages to process")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No new messages"})
            }
        
        # Get the last message
        last_update = updates[-1]
        logger.info(f"Processing last update: {json.dumps(last_update)}")
        
        message = last_update.get("message")
        if not message:
            logger.warning("Update does not contain a message")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Not a message update"})
            }
        
        # Extract message details
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        username = message.get("from", {}).get("username", "")
        text = message.get("text", "")
        
        logger.info(f"Message details - chat_id={chat_id}, user_id={user_id}, username={username}")
        logger.info(f"Message text: {text}")
        
        if not chat_id or not text:
            logger.warning("Message missing chat_id or text")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Invalid message format"})
            }
        
        # Handle the message
        handle_message(text, chat_id, user_id, username)
        
        logger.info("Message processed successfully")
        logger.info("=" * 80)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Message processed successfully",
                "user_id": user_id,
                "command": text.split()[0] if text else ""
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "details": str(e)
            })
        }