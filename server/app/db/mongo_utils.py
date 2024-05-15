from app.core.config import Settings
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

settings = Settings()


def get_db(mongo_engine : AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    db = mongo_engine[settings.MONGO_DB_NAME]
    return db

def get_collection(db : AsyncIOMotorDatabase, collection_name: Optional[str] = None) -> AsyncIOMotorCollection:
    if collection_name is None:
        collection_name = settings.MONGO_RSYNTH_COLLECTION_NAME
    collection = db[collection_name]
    return collection

async def find_one(collection : AsyncIOMotorCollection, query : dict, **kwargs) -> dict:
    result = await collection.find_one(query, **kwargs)
    return result

async def insert_one(collection : AsyncIOMotorCollection, data : dict) -> dict:
    result = await collection.insert_one(data)
    return result