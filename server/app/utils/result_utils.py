from app.core.config import Settings
from app.db.mongo_utils import find_one
from app.utils.s3_utils import create_presigned_url
from asyncio import gather

settings = Settings()

async def get_synth_result_from_mongo(synth_data, collection, s3_client):
    result = await find_one(collection, {"smile": synth_data.smile}, projection={"_id": False})
    if result is None:
        return {"code" : 102, "message": "Task not completed yet"}
    keys = [route["image_key"] for route in result["routes"]]
    urls = await gather(*[create_presigned_url(s3_client, key) for key in keys])
    urls  = [url.replace(settings.S3_ENDPOINT, settings.S3_REVERSE_PROXY) for url in urls]
    for idx, route in enumerate(result["routes"]):
        route["image_url"] = urls[idx]
    return {"code" : 200, "result" : result}

async def get_admet_result_from_mongo(synth_data, collection):
    result = await find_one(collection, {"smile": synth_data.smile}, projection={"_id": False})
    if result is None:
        return {"code" : 102, "message": "Task not completed yet"}
    return {"code" : 200, "result" : result}