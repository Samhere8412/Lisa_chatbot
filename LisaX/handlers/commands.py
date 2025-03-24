"""
Basic command handlers for the bot
"""

import time
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from db import add_user, get_users_count, get_chats_count
from config import WELCOME_MESSAGE, HELP_MESSAGE

# Start command handler
@filters.command("start")
async def start_command(client, message: Message):
    """Handle the /start command"""
    # Add user to database
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("📊 Stats", callback_data="stats")
            ]
        ]
    )
    
    # Send welcome message
    await message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=keyboard
    )

# Help command handler
@filters.command("help")
async def help_command(client, message: Message):
    """Handle the /help command"""
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("📊 Stats", callback_data="stats")
            ]
        ]
    )
    
    # Send help message
    await message.reply_text(
        HELP_MESSAGE,
        reply_markup=keyboard
    )

# Ping command handler
@filters.command("ping")
async def ping_command(client, message: Message):
    """Handle the /ping command to check bot latency"""
    # Calculate ping
    start_time = time.time()
    ping_message = await message.reply_text("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 2)
    
    # Send ping result
    await ping_message.edit_text(f"✅ Pong! `{ping_time}ms`")

# Stats command handler
@filters.command("stats")
async def stats_command(client, message: Message):
    """Handle the /stats command to show bot statistics"""
    # Get stats from database
    users_count = await get_users_count()
    chats_count = await get_chats_count()
    
    # Create stats message
    stats_text = f"""
📊 **Bot Statistics**

👥 Users: {users_count}
💬 Chats: {chats_count}
    """
    
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("📚 Help", callback_data="help")
            ]
        ]
    )
    
    # Send stats message
    await message.reply_text(
        stats_text,
        reply_markup=keyboard
    )

# Echo command handler
@filters.command("echo")
async def echo_command(client, message: Message):
    """Echo back the user's message"""
    # Check if message contains text to echo
    if len(message.command) < 2:
        await message.reply_text("Please provide text to echo.\nUsage: `/echo your text here`")
        return
    
    # Get the text to echo
    echo_text = message.text.split(maxsplit=1)[1]
    
    # Echo the text back
    await message.reply_text(echo_text)
