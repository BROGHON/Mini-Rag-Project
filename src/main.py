from fastapi import FastAPI
from routes import base, Data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app = FastAPI()

async def start_db_client():

    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient( settings.MONGODB_URL)
    app.db_client = app.mongo_conn[ settings.MONGODB_DATABASE]
#on events means you can make actions while events are running

    llm_provider_factory = LLMProviderFactory(settings)

    # generation client 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    #embbeding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID,
                                            embedding_size = settings.EMBEDDING_MODEL_EMBEDDING_SIZE
                                            ) 

async def shutdown_db_client():
    app.mongo_conn.close()

app.router.lifespan.on_startup.append(start_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)

app.include_router(base.base_router)
app.include_router(Data.data_router)

