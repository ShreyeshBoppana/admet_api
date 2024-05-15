from fastapi import APIRouter

from app.core.config import Settings
from app.core.database import mongo_db_engine
from app.db.mongo_utils import get_collection, get_db
from app.models.models import SearchRequest
from app.utils.result_utils import get_admet_result_from_mongo
from app.worker.admet_worker import admet_func, tiger

admet_router = router = APIRouter()

## Api endpoint to find reaction paths for a given molecule smile
settings = Settings()


@router.post("/admet_predict/")
async def admet_predict(synth_data: SearchRequest):
    admet_func.delay(synth_data.smile)
    len_queue = tiger.get_total_queue_size("default")
    return {"message": "Task added to queue", "length_queue": len_queue}


@router.post("/get_admet_result")
async def get_result(synth_data: SearchRequest):
    db_instance = get_db(mongo_db_engine)
    collection = get_collection(db_instance, settings.MONGO_ADMET_COLLECTION_NAME)
    result = await get_admet_result_from_mongo(synth_data, collection)
    return result
