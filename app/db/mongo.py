import os
from typing import TYPE_CHECKING

from pymongo import MongoClient

if TYPE_CHECKING:
    from pymongo.database import Database

client: 'MongoClient' = None
db: 'Database' = None


def setup_mongo():
    global client
    global db

    # Get environment variables
    db_name = os.getenv('DB_NAME', 'db') if not os.getenv('TEST_ENV') else os.getenv('TEST_DB_NAME', 'test_db')

    if os.getenv('MONGO_URI'):
        mongo_uri = os.getenv('MONGO_URI')
    else:
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', 27017))
        db_username = os.getenv('DB_USERNAME')
        db_password = os.getenv('DB_PASSWORD')

        # Construct the MongoDB URI with authentication
        if db_username and db_password:
            mongo_uri = f"mongodb://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            mongo_uri = f"mongodb://{db_host}:{db_port}/{db_name}"

    client = MongoClient(mongo_uri)
    db = client[db_name]


def get_db():
    global db
    if db is None:
        setup_mongo()
    return db
