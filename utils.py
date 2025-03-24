import os
import time
import logging
import asyncio
import subprocess
from functools import wraps
from pyrogram.types import Message

logger = logging.getLogger(__name__)

def get_readable_time(seconds: int) -> str:
    """Convert seconds to readable time format"""
    count = 0
    time_formats = ["{} days", "{} hours", "{} minutes", "{} seconds"]
    time_values = []
    
    # Calculate days
    if seconds >= 86400:  # 60 * 60 * 24
        days = seconds // 86400
        seconds %= 86400
        time_values.append(days)
        count += 1
    else:
        time_values.append(0)
        count += 1
    
    # Calculate hours
    if seconds >= 3600:  # 60 * 60
        hours = seconds // 3600
        seconds %= 3600
        time_values.append(hours)
        count += 1
    else:
        time_values.append(0)
        count += 1
    
    # Calculate minutes
    if seconds >= 60:
        minutes = seconds // 60
        seconds %= 60
        time_values.append(minutes)
        count += 1
    else:
        time_values.append(0)
        count += 1
    
    # Remaining seconds
    time_values.append(seconds)
    count += 1
    
    # Format the time string
    time_string = ""
    for i in range(count):
        if time_values[i] > 0:
            time_string += time_formats[i].format(time_values[i]) + ", "
    
    # Remove the trailing comma and space
    if time_string:
        time_string = time_string[:-2]
    else:
        time_string = "0 seconds"
    
    return time_string

def get_readable_file_size(size_in_bytes: int) -> str:
    """Convert bytes to readable file size"""
    if size_in_bytes is None:
        return "0B"
    
    # Size conversion constants
    size_units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size_index = 0
    
    # Convert to appropriate unit
    size = float(size_in_bytes)
    while size >= 1024 and size_index < len(size_units) - 1:
        size /= 1024
        size_index += 1
    
    # Format the size string
    if size_index == 0:
        return f"{int(size)} {size_units[size_index]}"
    else:
        return f"{size:.2f} {size_units[size_index]}"

def is_admin(func):
    """Decorator to check if user is admin"""
    @wraps(func)
    async def wrapper(client, message: Message):
        # Check if the user is the bot owner
        from config import OWNER_ID
        if message.from_user.id == OWNER_ID:
            return await func(client, message)
        
        # If it's a private chat and not the owner, deny access
        if message.chat.type == "private":
            await message.reply_text("🚫 This command is only available to the bot owner.")
            return
        
        # Check if user is admin in the group
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status in ["creator", "administrator"]:
            return await func(client, message)
        else:
            await message.reply_text("🚫 This command is only available to group admins.")
            return
    
    return wrapper

async def run_command(command):
    """Run a shell command and return output"""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Command '{command}' failed with return code {process.returncode}")
            logger.error(f"Stderr: {stderr.decode()}")
            return False, stderr.decode()
        
        return True, stdout.decode()
    except Exception as e:
        logger.error(f"Error running command '{command}': {e}")
        return False, str(e)
