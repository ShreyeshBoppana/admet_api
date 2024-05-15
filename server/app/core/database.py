from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import Settings


settings = Settings()

mongo_url = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}"

settings = Settings()

def get_mongo_client() -> AsyncIOMotorClient:
    mongo_engine = AsyncIOMotorClient(mongo_url)
    return mongo_engine


def get_worker_monogo_client() -> MongoClient:
    mongo_engine = MongoClient(mongo_url)
    return mongo_engine

mongo_db_engine = get_mongo_client()