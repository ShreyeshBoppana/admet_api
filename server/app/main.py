import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.routers.admet import admet_router
from app.api.api_v1.routers.retro_synth import reverse_synth_router
from app.core.config import Settings

# TODO: Change this to best practice for creating all the DB tables
# from app.db.session import Base, engine

# # @lru_cache() modifies the function it decorates to return the same value that was returned the first time,
# # instead of computing it again, executing the code of the function every time.
# @lru_cache()
# def get_settings():
#     settings = Settings()

settings = Settings()

app = FastAPI(title=settings.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api")


# Add Processing time to the response header for each request
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Creates the database tables required for the application
# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Server startup event
@app.on_event("startup")
def startup_event():
    # create_db_and_tables()
    pass


# Routers
app.include_router(
    reverse_synth_router,
    prefix=settings.API_V1_STR,
    tags=["Reverse Synthesis"],
    # dependencies=[Depends(get_current_active_user)],
)

app.include_router(
    admet_router,
    prefix=settings.API_V1_STR,
    tags=["ADMET Prediction"],
    # dependencies=[Depends(get_current_active_user)],
)
