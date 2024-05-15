from fastapi import APIRouter
from app.models.models import SearchRequest
from app.db.mongo_utils import get_db, get_collection
from app.core.database import mongo_db_engine
from app.utils.s3_utils import s3_session
from app.utils.result_utils import get_synth_result_from_mongo
from app.worker.retro_worker import retro_func, tiger
from app.core.config import Settings

reverse_synth_router = router = APIRouter()
settings = Settings()

## Api endpoint to find reaction paths for a given molecule smile
@router.post("/synth/")
async def synth(synth_data: SearchRequest):
    retro_func.delay(synth_data.smile)
    len_queue = tiger.get_total_queue_size("default")
    return {"message": "Task added to queue", "length_queue": len_queue}

@router.post("/get_synth_result")
async def get_result(synth_data: SearchRequest):
    db_instance = get_db(mongo_db_engine)
    collection = get_collection(db_instance, settings.MONGO_RSYNTH_COLLECTION_NAME)
    async with s3_session.create_client('s3', 
                                    region_name=settings.S3_REGION, 
                                    endpoint_url=settings.S3_ENDPOINT, 
                                    aws_access_key_id=settings.S3_KEY,
                                    aws_secret_access_key=settings.S3_SECRET) as s3_client:
        result = await get_synth_result_from_mongo(synth_data, collection, s3_client)
    return result