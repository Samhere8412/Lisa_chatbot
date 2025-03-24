from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db import get_users_count, get_chats_count
from config import WELCOME_MESSAGE, HELP_MESSAGE
from LisaX import bot

# Handle all callback queries
@bot.on_callback_query()
async def handle_callback_query(client, callback_query: CallbackQuery):
    """Handle callback queries from inline buttons"""
    # Get callback data
    data = callback_query.data
    
    # Handle based on callback data
    if data == "start":
        # Show start message
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📚 Help", callback_data="help"),
                    InlineKeyboardButton("📊 Stats", callback_data="stats")
                ]
            ]
        )
        
        await callback_query.edit_message_text(
            WELCOME_MESSAGE,
            reply_markup=keyboard
        )
        
    elif data == "help":
        # Show help message
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("📊 Stats", callback_data="stats")
                ]
            ]
        )
        
        await callback_query.edit_message_text(
            HELP_MESSAGE,
            reply_markup=keyboard
        )
        
    elif data == "stats":
        # Show stats message
        users_count = await get_users_count()
        chats_count = await get_chats_count()
        
        stats_text = f"""
📊 **Bot Statistics**

👥 Users: {users_count}
💬 Chats: {chats_count}
        """
        
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("📚 Help", callback_data="help")
                ]
            ]
        )
        
        await callback_query.edit_message_text(
            stats_text,
            reply_markup=keyboard
        )
        
    else:
        # Unknown callback data, just answer the callback
        await callback_query.answer("Unknown button action")
    
    # Always answer the callback query to remove the loading state
    await callback_query.answer()
