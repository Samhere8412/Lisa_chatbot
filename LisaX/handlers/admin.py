import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from db import get_all_users, get_all_chats, get_users_count, get_chats_count
from utils import is_admin, get_readable_time
from config import OWNER_ID
from LisaX import bot

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
