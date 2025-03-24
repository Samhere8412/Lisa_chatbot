import os
import sys
import time
import logging
from LisaX import bot
from db import create_indexes, update_bot_stats

# Import handlers explicitly here
import LisaX.handlers.commands
import LisaX.handlers.callback
import LisaX.handlers.messages
import LisaX.handlers.admin

logger = logging.getLogger(__name__)

async def main():
    """Start the bot and set up the database"""
    try:
        # Start the bot
        await bot.start()
        
        # Get bot information
        bot_info = await bot.get_me()
        logger.info(f"Bot started as @{bot_info.username}")
        
        # Create database indexes
        await create_indexes()
        
        # Update bot stats
        await update_bot_stats(bot)
        
        # Log startup time
        start_time = time.time()
        logger.info(f"Bot startup completed in {time.time() - start_time:.2f} seconds")
        
        # Idle the bot to keep it running
        await bot.idle()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        
    finally:
        # Properly close the bot client when exiting
        if bot:
            await bot.stop()
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
