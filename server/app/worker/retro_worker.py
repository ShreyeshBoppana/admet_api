import io
from uuid import uuid4

import tasktiger
from botocore.session import get_session

from app.core.config import Settings
from app.core.database import get_worker_monogo_client
from app.utils.worker_utils import redis_connection

settings = Settings()
retro_mongo_collection = get_worker_monogo_client()[settings.MONGO_DB_NAME][
    settings.MONGO_RSYNTH_COLLECTION_NAME
]
tiger = tasktiger.TaskTiger(connection=redis_connection)

filename = settings.AIZYNTHFINDER_CONFIG_FILE


def image_to_byte_array(image) -> bytes:
    # BytesIO is a file-like buffer stored in memory
    imgByteArr = io.BytesIO()
    # image.save expects a file-like as a argument
    image.save(imgByteArr, format="png")
    # Turn the BytesIO object back into a bytes object
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def reverse_synth(smile):
    from aizynthfinder.aizynthfinder import AiZynthFinder

    aizyth_app = AiZynthFinder(configfile=filename)
    aizyth_app.stock.select("zinc")
    aizyth_app.expansion_policy.select("uspto")
    aizyth_app.filter_policy.select("uspto")
    aizyth_app.target_smiles = smile
    aizyth_app.tree_search()
    aizyth_app.build_routes()
    routes_data = []
    for route in aizyth_app.routes:
        reaction_dict = route["reaction_tree"].to_dict().copy()
        reaction_dict["score"] = route["score"]
        reaction_image = route["reaction_tree"].to_image()
        imgByteArr = image_to_byte_array(reaction_image)
        routes_data.append((reaction_dict, imgByteArr))
    return routes_data


def save_routes_data(routes, smile):
    result = [0] * len(routes)
    file_names_data = [0] * len(routes)
    session = get_session()
    client = session.create_client(
        "s3",
        region_name=settings.S3_REGION,
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_KEY,
        aws_secret_access_key=settings.S3_SECRET,
    )
    for idx, route_data in enumerate(routes):
        reaction_dict, reaction_image = route_data
        file_name = str(uuid4()) + ".png"
        file_names_data.append((file_name, reaction_image))
        image_path = file_name
        reaction_dict["image_key"] = image_path
        result[idx] = reaction_dict
        _ = client.put_object(
            Bucket=settings.S3_BUCKET_NAME, Key=file_name, Body=reaction_image
        )
    retro_mongo_collection.insert_one({"smile": smile, "routes": result})


@tiger.task(unique=True)
def retro_func(smile):
    result_smile = retro_mongo_collection.find_one(
        {"smile": smile}, projection={"_id": False}
    )
    if result_smile is None:
        routes = reverse_synth(smile)
        save_routes_data(routes, smile=smile)
    return smile
