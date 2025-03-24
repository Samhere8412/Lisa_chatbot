#!/usr/bin/env python3
"""
LisaX Bot - A simple Telegram bot built with Pyrogram and MongoDB
Run this file to start the bot directly
"""

import os
import sys
import logging
import asyncio
from LisaX import bot
from LisaX.__main__ import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LisaXBot")

if __name__ == "__main__":
    try:
        logger.info("Starting LisaX Bot...")
        
        # Check if bot is initialized
        if not bot:
            logger.critical("Bot client not initialized. Please check your environment variables.")
            sys.exit(1)
        
        # Run the bot
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)
