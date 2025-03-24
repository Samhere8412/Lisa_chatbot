from pyrogram import Client
import logging
from config import API_ID, API_HASH, BOT_TOKEN
from db import init_db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LisaX")

# Initialize database
init_db()

# Initialize the bot
bot = Client(
    "LisaXBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Import handlers
from LisaX.handlers import admin, callback, commands, messages
