
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "CodeAthonDB")

client = None
db = None

if MONGO_URI:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )
    db = client[MONGO_DB]


def check_database_connection():
    """Check whether MongoDB is reachable."""
    if db is None:
        return False

    try:
        db.command("ping")
        return True
    except PyMongoError:
        return False