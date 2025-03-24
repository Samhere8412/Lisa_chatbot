#!/usr/bin/env python3
"""
LisaX Bot - A Telegram bot built with Pyrogram
"""
import asyncio
import logging
import os
from pyrogram import Client
from pyrogram.enums import ParseMode
from dotenv import load_dotenv
from config import API_ID, API_HASH, BOT_TOKEN
from db import init_db, create_indexes, update_bot_stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LisaXBot")

# Create the bot client
bot = Client(
    "LisaXBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

# Import handlers - this must be done after creating the bot instance
from handlers import *

async def main():
    """Start the bot and set up the database"""
    try:
        logger.info("Initializing database...")
        init_db()
        
        logger.info("Starting bot...")
        await bot.start()
        
        # Get bot information
        bot_info = await bot.get_me()
        logger.info(f"Bot started as @{bot_info.username}")
        
        # Create database indexes
        await create_indexes()
        
        # Update bot stats
        await update_bot_stats(bot)
        
        logger.info("Bot is now running...")
        await bot.idle()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        # Always properly close the bot client when exiting
        if bot:
            await bot.stop()

if __name__ == "__main__":
    # Use asyncio.run to handle the event loop properly
    asyncio.run(main())
