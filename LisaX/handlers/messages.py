from pyrogram import filters
from pyrogram.types import Message
from db import add_user, add_chat
from config import DEFAULT_WELCOME_MESSAGE
from LisaX import bot

# Handle private messages (all messages that are not commands)
@bot.on_message(filters.private & ~filters.command([]))
async def handle_private_message(client, message: Message):
    """Handle private messages"""
    # Add user to database
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # For now, we're not replying to regular messages to avoid spamming the user

# Handle group messages (all messages that are not commands)
@bot.on_message(filters.group & ~filters.command([]))
async def handle_group_message(client, message: Message):
    """Handle group messages"""
    # Add chat to database
    await add_chat(
        chat_id=message.chat.id,
        title=message.chat.title,
        chat_type=message.chat.type
    )
    
    # If the user exists, add them to the database
    if message.from_user:
        await add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

# Welcome new members
@bot.on_message(filters.new_chat_members)
async def welcome_new_members(client, message: Message):
    """Welcome new members in groups"""
    # Get bot's user ID
    me = await client.get_me()
    
    # Check if the bot was added to a new group
    for new_member in message.new_chat_members:
        if new_member.id == me.id:
            # Bot was added to a new group
            await add_chat(
                chat_id=message.chat.id,
                title=message.chat.title,
                chat_type=message.chat.type
            )
            
            # Send a greeting message
            await message.reply_text(f"Thanks for adding me to the group! Use /help to see available commands.")
            return
        
    # Welcome regular new users
    names = [user.first_name for user in message.new_chat_members]
    welcome_text = DEFAULT_WELCOME_MESSAGE
    
    if len(names) == 1:
        welcome_text = f"Welcome, {names[0]}! 👋"
    elif len(names) > 1:
        formatted_names = ", ".join(names[:-1]) + f" and {names[-1]}"
        welcome_text = f"Welcome, {formatted_names}! 👋"
    
    await message.reply_text(welcome_text)
