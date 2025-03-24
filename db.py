import os
import time
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Database connection
client = None
db = None
users_collection = None
chats_collection = None
bot_stats_collection = None

def init_db():
    """Initialize database connection and collections"""
    global client, db, users_collection, chats_collection, bot_stats_collection
    
    # Get MongoDB connection string from environment variable or use default
    mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Ping the server to confirm connection
        client.admin.command('ping')
        
        logger.info("Connected to MongoDB")
        
        # Get database
        db = client.lisax
        
        # Get collections
        users_collection = db.users
        chats_collection = db.chats
        bot_stats_collection = db.bot_stats
        
        # Return true if successful
        return True
        
    except ServerSelectionTimeoutError:
        logger.error("Could not connect to MongoDB server. Please check your connection string and ensure MongoDB is running.")
        return False
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return False

async def create_indexes():
    """Create indexes for collections"""
    # Indexes for users collection
    await users_collection.create_index("user_id", unique=True)
    await users_collection.create_index("username")
    
    # Indexes for chats collection
    await chats_collection.create_index("chat_id", unique=True)
    
    logger.info("Database indexes created")

async def add_user(user_id, username=None, first_name=None, last_name=None):
    """Add or update a user in the database"""
    try:
        # Prepare user data
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_seen": time.time()
        }
        
        # Update user data or insert if not exists
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True
        )
        
        return True
    except Exception as e:
        logger.error(f"Error adding user {user_id} to database: {e}")
        return False

async def add_chat(chat_id, title=None, chat_type=None):
    """Add or update a chat in the database"""
    try:
        # Prepare chat data
        chat_data = {
            "chat_id": chat_id,
            "title": title,
            "chat_type": chat_type,
            "last_interaction": time.time()
        }
        
        # Update chat data or insert if not exists
        await chats_collection.update_one(
            {"chat_id": chat_id},
            {"$set": chat_data},
            upsert=True
        )
        
        return True
    except Exception as e:
        logger.error(f"Error adding chat {chat_id} to database: {e}")
        return False

async def get_user(user_id):
    """Get user data from the database"""
    try:
        return await users_collection.find_one({"user_id": user_id})
    except Exception as e:
        logger.error(f"Error getting user {user_id} from database: {e}")
        return None

async def get_chat(chat_id):
    """Get chat data from the database"""
    try:
        return await chats_collection.find_one({"chat_id": chat_id})
    except Exception as e:
        logger.error(f"Error getting chat {chat_id} from database: {e}")
        return None

async def get_all_users():
    """Get all users from the database"""
    try:
        return await users_collection.find().to_list(length=None)
    except Exception as e:
        logger.error(f"Error getting users from database: {e}")
        return []

async def get_all_chats():
    """Get all chats from the database"""
    try:
        return await chats_collection.find().to_list(length=None)
    except Exception as e:
        logger.error(f"Error getting chats from database: {e}")
        return []

async def get_users_count():
    """Get the count of users"""
    try:
        return await users_collection.count_documents({})
    except Exception as e:
        logger.error(f"Error getting users count: {e}")
        return 0

async def get_chats_count():
    """Get the count of chats"""
    try:
        return await chats_collection.count_documents({})
    except Exception as e:
        logger.error(f"Error getting chats count: {e}")
        return 0

async def update_bot_stats(bot):
    """Update bot statistics in the database"""
    try:
        # Get bot info
        bot_info = await bot.get_me()
        
        # Get database statistics
        users_count = await get_users_count()
        chats_count = await get_chats_count()
        
        # Prepare stats data
        stats_data = {
            "timestamp": time.time(),
            "bot_id": bot_info.id,
            "bot_username": bot_info.username,
            "users_count": users_count,
            "chats_count": chats_count
        }
        
        # Update stats or insert if not exists
        await bot_stats_collection.update_one(
            {"bot_id": bot_info.id},
            {"$set": stats_data},
            upsert=True
        )
        
        logger.debug("Bot stats updated")
        return True
    except Exception as e:
        logger.error(f"Error updating bot stats: {e}")
        return False

def get_db_stats():
    """Get database statistics for the web interface"""
    try:
        if db is None:
            return {
                "status": "disconnected",
                "users_count": 0,
                "chats_count": 0
            }
            
        return {
            "status": "connected",
            "users_count": 0,  # Will be updated asynchronously
            "chats_count": 0   # Will be updated asynchronously
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
