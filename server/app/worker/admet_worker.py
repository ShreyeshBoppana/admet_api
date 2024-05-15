import time

import tasktiger

from app.core.config import Settings
from app.core.database import get_worker_monogo_client
from app.utils.worker_utils import redis_connection

settings = Settings()
tiger = tasktiger.TaskTiger(connection=redis_connection)
admet_mongo_collection = get_worker_monogo_client()[settings.MONGO_DB_NAME][
    settings.MONGO_ADMET_COLLECTION_NAME
]
STATIC_DIRECTION = settings.ADMET_MODEL_FOLDER


def admet_predict(smiles):
    import xgboost

    from app.worker.admet_utils import featurize, get_colors, properties

    """
    ADMET prediction
    """
    features = featurize(smiles)

    names = [
        "caco2_wang",
        "bioavailability_ma",
        "lipophilicity_astrazeneca",
        "solubility_aqsoldb",
        "hia_hou",
        "pgp_broccatelli",
        "bbb_martins",
        "ppbr_az",
        "vdss_lombardo",
        "cyp2d6_veith",
        "cyp3a4_veith",
        "cyp2c9_veith",
        "cyp2c9_substrate_carbonmangels",
        "cyp2d6_substrate_carbonmangels",
        "cyp3a4_substrate_carbonmangels",
        "half_life_obach",
        "clearance_microsome_az",
        "clearance_hepatocyte_az",
        "ld50_zhu",
        "herg",
        "ames",
        "dili",
    ]

    percent_names = [
        "hia_hou",
        "pgp_broccatelli",
        "bioavailability_ma",
        "bbb_martins",
        "cyp2c9_veith",
        "cyp2d6_veith",
        "cyp3a4_veith",
        "cyp2c9_substrate_carbonmangels",
        "cyp2d6_substrate_carbonmangels",
        "cyp3a4_substrate_carbonmangels",
        "herg",
        "ames",
        "dili",
    ]

    results = {}
    results["smiles"] = smiles

    # timestamp as file name
    timestamp = time.time()
    results["timestamp"] = timestamp

    xgb = xgboost.XGBRegressor(verbosity=0, silent=False)

    for name in names:
        xgb.load_model(STATIC_DIRECTION + "/" + name + ".json")
        results[name] = xgb.predict(features)[0]
        if name in percent_names:
            results[name] *= 100
        results[name] = round(results[name], 2)

    # calculate properties
    property_values = properties(smiles)

    # predict ADMET
    property_names = [
        "numHAcceptors",
        "numHDonors",
        "logp",
        "weight",
        "heter",
        "rot",
        "ring",
    ]
    for name, val in zip(property_names, property_values):
        results[name] = val

    # get color codes
    results = get_colors(results)

    return results


def save_admet_data(admet_result, smile):
    from app.worker.admet_utils import correct_encoding

    admet_result = correct_encoding(admet_result)
    admet_mongo_collection.insert_one({"smile": smile, "result": admet_result})


@tiger.task(unique=True)
def admet_func(smile):
    result_smile = admet_mongo_collection.find_one(
        {"smile": smile}, projection={"_id": False}
    )
    if result_smile is None:
        routes = admet_predict(smile)
        save_admet_data(routes, smile=smile)
    return smile
