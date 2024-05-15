from pydantic import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "Reverse-Synth Server"
    API_V1_STR: str = "/api/v1"
    MODE: str = "development"

    ##### DATABASE PARAMS #####
    MONGO_HOST = "mongodb"
    MONGO_PORT = 27017
    MONGO_USER = "root"
    MONGO_PASSWORD = "example"
    MONGO_DB_NAME = "retro_syth"
    MONGO_RSYNTH_COLLECTION_NAME = "synth_data"
    MONGO_ADMET_COLLECTION_NAME = "admet_data"

    ##### REDIS PARAMS #####
    REDIS_HOST = "redis"
    REDIS_PORT = 6379

    ##### S3 PARAMS #####
    S3_ENDPOINT = "http://minio:9000"
    S3_KEY = "minio"
    S3_SECRET = "password"
    S3_SECURE = False
    S3_REGION = "us-east-1"
    S3_BUCKET_NAME = "reverse-synth"
    S3_REVERSE_PROXY = "https://rsynth.paultharun.com/files"

    ## AiZynthFinder config file
    AIZYNTHFINDER_CONFIG_FILE = "/model_files/config.yml"

    ## Admet Config
    ADMET_MODEL_FOLDER = "/model_files/admet"

    # CORS PARAMS
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    class Config:
        env_file = ".env"
