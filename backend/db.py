import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
DB_NAME = "leetcodedata"

if not mongodb_uri:
    raise ValueError("MONGODB_URI environment variable is required")

# Singleton client
_client = None

def get_mongo_client():
    global _client
    if _client is None:
        _client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    return _client

def get_db():
    """Get leetcodedata database."""
    return get_mongo_client()[DB_NAME]

def check_mongodb_connection():
    """Check MongoDB connection."""
    try:
        client = get_mongo_client()
        client.server_info()  # Force connection
        logger.info("MongoDB connection successful")
        return True
    except (ConnectionFailure, ConfigurationError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False

def drop_collection(collection_name):
    """Drop a collection."""
    try:
        db = get_db()
        db[collection_name].drop()
        logger.info(f"Collection '{collection_name}' dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping collection '{collection_name}': {e}")

def insert_data(collection_name, data, batch_size=200):
    """
    Insert data into MongoDB, optionally in batches.
    """
    try:
        db = get_db()
        drop_collection(collection_name)  # As per original behavior
        total_records = len(data)
        logger.info(f"Inserting {total_records} records into '{collection_name}'...")

        if batch_size >= total_records:
            db[collection_name].insert_many(data)
            logger.info(f"All {total_records} records inserted into '{collection_name}'")
        else:
            for i in range(0, total_records, batch_size):
                batch = data[i:i + batch_size]
                db[collection_name].insert_many(batch)
                logger.info(f"Inserted batch {i}-{i+len(batch)-1}")

        create_indexes(collection_name)
    except Exception as e:
        logger.error(f"Error inserting data into '{collection_name}': {e}")
        raise

def create_indexes(collection_name):
    """Create indexes on specified fields."""
    indexes = ["DEPT", "GENDER", "BATCH", "Problem Count", "Contest Rating"]
    db = get_db()
    for field in indexes:
        try:
            db[collection_name].create_index(field)
            logger.info(f"Index on '{field}' created successfully")
        except Exception as e:
            logger.warning(f"Index on '{field}' already exists or failed: {e}")
