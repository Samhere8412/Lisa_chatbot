"""
All bot handlers in one file to avoid import issues
"""
import time
import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from main import bot
from db import add_user, add_chat, get_users_count, get_chats_count, get_all_users, get_all_chats
from utils import is_admin, get_readable_time
from config import WELCOME_MESSAGE, HELP_MESSAGE, DEFAULT_WELCOME_MESSAGE, OWNER_ID

######################
# Command handlers
######################

# Start command handler
@bot.on_message(filters.command("start"))
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
@bot.on_message(filters.command("help"))
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
@bot.on_message(filters.command("ping"))
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
@bot.on_message(filters.command("stats"))
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
@bot.on_message(filters.command("echo"))
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

######################
# Admin commands
######################

# Broadcast command handler
@bot.on_message(filters.command("broadcast"))
@is_admin
async def broadcast_command(client, message: Message):
    """Broadcast a message to all users (admin only)"""
    # Check if the message has text to broadcast
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Please provide text to broadcast or reply to a message.\n"
            "Usage: `/broadcast your message here`"
        )
        return
    
    # Get the message text to broadcast
    if message.reply_to_message:
        # Use the replied message as broadcast content
        broadcast_message = message.reply_to_message
    else:
        # Use the command text as broadcast content
        broadcast_text = message.text.split(maxsplit=1)[1]
        broadcast_message = await message.reply_text(broadcast_text)
    
    # Get all users
    users = await get_all_users()
    total_users = len(users)
    
    if total_users == 0:
        await message.reply_text("No users found in database.")
        return
    
    # Send the initial status message
    status_msg = await message.reply_text(
        f"Broadcasting message to {total_users} users..."
    )
    
    # Counters for tracking progress
    success = 0
    failed = 0
    
    # Start time for ETA calculation
    start_time = asyncio.get_event_loop().time()
    
    # Define the status update coroutine
    async def update_status():
        """Update the status message periodically"""
        nonlocal status_msg
        nonlocal success
        nonlocal failed
        
        while success + failed < total_users:
            # Calculate progress
            progress = (success + failed) / total_users * 100
            
            # Calculate ETA
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if success + failed > 0:
                items_per_second = (success + failed) / elapsed_time
                remaining_items = total_users - (success + failed)
                eta_seconds = remaining_items / items_per_second if items_per_second > 0 else 0
                eta = get_readable_time(int(eta_seconds))
            else:
                eta = "Unknown"
            
            # Update status message
            await status_msg.edit_text(
                f"Broadcasting message to {total_users} users...\n\n"
                f"Progress: {progress:.1f}% ({success + failed}/{total_users})\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}\n"
                f"⏱️ ETA: {eta}"
            )
            
            # Wait before next update
            await asyncio.sleep(3)
    
    # Start the status update task
    status_update_task = asyncio.create_task(update_status())
    
    # Perform the broadcast
    for user in users:
        try:
            if message.reply_to_message:
                # Forward the original message
                await message.reply_to_message.forward(user["user_id"])
            else:
                # Send as a new message
                await client.send_message(
                    user["user_id"],
                    broadcast_text
                )
            success += 1
        except FloodWait as e:
            # Handle Telegram's flood wait
            await asyncio.sleep(e.x)
            
            # Try again after the wait
            try:
                if message.reply_to_message:
                    await message.reply_to_message.forward(user["user_id"])
                else:
                    await client.send_message(
                        user["user_id"],
                        broadcast_text
                    )
                success += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
        
        # Small delay between messages to avoid hitting limits
        await asyncio.sleep(0.1)
    
    # Cancel the status update task
    status_update_task.cancel()
    
    # Calculate completion time
    completion_time = asyncio.get_event_loop().time() - start_time
    readable_time = get_readable_time(int(completion_time))
    
    # Send final report
    await status_msg.edit_text(
        f"✅ Broadcast completed in {readable_time}\n\n"
        f"Total users: {total_users}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
    )

# Chat broadcast command handler
@bot.on_message(filters.command("chatbroadcast"))
@is_admin
async def chat_broadcast_command(client, message: Message):
    """Broadcast a message to all chats (admin only)"""
    # Check if the message has text to broadcast
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Please provide text to broadcast or reply to a message.\n"
            "Usage: `/chatbroadcast your message here`"
        )
        return
    
    # Get the message text to broadcast
    if message.reply_to_message:
        # Use the replied message as broadcast content
        broadcast_message = message.reply_to_message
    else:
        # Use the command text as broadcast content
        broadcast_text = message.text.split(maxsplit=1)[1]
        broadcast_message = await message.reply_text(broadcast_text)
    
    # Get all chats
    chats = await get_all_chats()
    total_chats = len(chats)
    
    if total_chats == 0:
        await message.reply_text("No chats found in database.")
        return
    
    # Send the initial status message
    status_msg = await message.reply_text(
        f"Broadcasting message to {total_chats} chats..."
    )
    
    # Counters for tracking progress
    success = 0
    failed = 0
    
    # Start time for ETA calculation
    start_time = asyncio.get_event_loop().time()
    
    # Define the status update coroutine
    async def update_status():
        """Update the status message periodically"""
        nonlocal status_msg
        nonlocal success
        nonlocal failed
        
        while success + failed < total_chats:
            # Calculate progress
            progress = (success + failed) / total_chats * 100
            
            # Calculate ETA
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if success + failed > 0:
                items_per_second = (success + failed) / elapsed_time
                remaining_items = total_chats - (success + failed)
                eta_seconds = remaining_items / items_per_second if items_per_second > 0 else 0
                eta = get_readable_time(int(eta_seconds))
            else:
                eta = "Unknown"
            
            # Update status message
            await status_msg.edit_text(
                f"Broadcasting message to {total_chats} chats...\n\n"
                f"Progress: {progress:.1f}% ({success + failed}/{total_chats})\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}\n"
                f"⏱️ ETA: {eta}"
            )
            
            # Wait before next update
            await asyncio.sleep(3)
    
    # Start the status update task
    status_update_task = asyncio.create_task(update_status())
    
    # Perform the broadcast
    for chat in chats:
        try:
            if message.reply_to_message:
                # Forward the original message
                await message.reply_to_message.forward(chat["chat_id"])
            else:
                # Send as a new message
                await client.send_message(
                    chat["chat_id"],
                    broadcast_text
                )
            success += 1
        except FloodWait as e:
            # Handle Telegram's flood wait
            await asyncio.sleep(e.x)
            
            # Try again after the wait
            try:
                if message.reply_to_message:
                    await message.reply_to_message.forward(chat["chat_id"])
                else:
                    await client.send_message(
                        chat["chat_id"],
                        broadcast_text
                    )
                success += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
        
        # Small delay between messages to avoid hitting limits
        await asyncio.sleep(0.1)
    
    # Cancel the status update task
    status_update_task.cancel()
    
    # Calculate completion time
    completion_time = asyncio.get_event_loop().time() - start_time
    readable_time = get_readable_time(int(completion_time))
    
    # Send final report
    await status_msg.edit_text(
        f"✅ Broadcast completed in {readable_time}\n\n"
        f"Total chats: {total_chats}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
    )

# Admin stats command handler
@bot.on_message(filters.command("adminstats"))
@is_admin
async def admin_stats_command(client, message: Message):
    """Get detailed bot statistics (admin only)"""
    # Get stats from database
    users_count = await get_users_count()
    chats_count = await get_chats_count()
    
    # Get bot uptime
    bot_uptime = "Not implemented yet"
    
    # Create stats message
    stats_text = f"""
📊 **Detailed Bot Statistics**

👥 Users: {users_count}
💬 Chats: {chats_count}
⏱️ Uptime: {bot_uptime}

🔐 **Admin Info**
🆔 Your ID: `{message.from_user.id}`
    """
    
    # Send stats message
    await message.reply_text(stats_text)

######################
# Message handlers
######################

# Handle private messages (all messages that are not commands)
@bot.on_message(filters.private & ~filters.command(["start", "help", "ping", "stats", "echo", "broadcast", "chatbroadcast", "adminstats"]))
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
@bot.on_message(filters.group & ~filters.command(["start", "help", "ping", "stats", "echo", "broadcast", "chatbroadcast", "adminstats"]))
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

######################
# Callback handlers
######################

# Handle all callback queries
@bot.on_callback_query()
async def handle_callback_query(client, callback_query):
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
