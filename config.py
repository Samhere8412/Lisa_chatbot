import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Bot version
VERSION = "1.0.0"

# API credentials from environment variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Bot information
BOT_USERNAME = os.environ.get("BOT_USERNAME", "LisaXBot")  # Default value, will be updated from bot.get_me()

# Owner information
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "")

# MongoDB
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

# Messages
WELCOME_MESSAGE = """
👋 Welcome to LisaX Bot!

I'm a powerful Telegram bot built with Pyrogram and MongoDB.

Use /help to see available commands.
"""

HELP_MESSAGE = """
📚 **Available Commands**

**Basic Commands:**
/start - Start the bot
/help - Show this help message
/ping - Check bot latency
/stats - Show bot statistics
/echo - Echo a message

**Admin Commands:**
/broadcast - Broadcast a message to all users
/chatbroadcast - Broadcast a message to all chats
/adminstats - Show detailed bot statistics

Made with ❤️ by @{}
""".format(OWNER_USERNAME)

# Customization
DEFAULT_WELCOME_MESSAGE = "Welcome to the group! 👋"
