import asyncio
from contextlib import asynccontextmanager
#import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import Union
from dotenv import load_dotenv
import src
from src import APP_ENV
from src import telemetry
from src.logger import logger
from src.log_middleware import log_middleware
import httpx

#Load .env vars
load_dotenv()

# Startup event
async def startup(app: FastAPI):
    logger.info(f"Starting up... {APP_ENV}")

#Shutdown event
async def shutdown(app: FastAPI):
    logger.info("Shutting down...")
    close_jobs = []
    telemetry.dismount_telemetry(app)
    await asyncio.gather(*close_jobs)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup(app)
    yield
    await shutdown(app)

#Init FastAPI app
app = FastAPI(
    title=src.PACKAGE_NAME,
    version=src.__version__,
    contact={src.__author__: src.__author_email__},
    description=src.__description__,
    lifespan=lifespan,
    debug=APP_ENV != "prod"
)

#Add middlewares
#TODO: add CORSMiddleware, GZipMiddleware, ...
"""
This is a way you can extract your middleware into its own 
module (file) and register that middleware to the app object
"""
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

# Instrument FastAPI app with OpenTelemetry
telemetry.mount_telemetry(app)

logger.info('Starting API...')

################################################################################
#Pydantic
class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None
################################################################################
#Routes
#TODO: add OTLP manual metric instrumentation
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/ping")
async def ping():
    return {"response": "pong"}

# Nested GET request route
@app.get("/nested-request")
async def nested_request():
    async with httpx.AsyncClient() as client:
        try:
            await asyncio.sleep(3)
            response = await client.get("http://localhost:8000/ping")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch /ping")
            return {"nested_response": response.json()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/send")
async def send_things(my_object: Item):
    #add artifical post time to show logging process time delta
    await asyncio.sleep(1.5)
    
    return {
        "status": "ok",
        "received_object": my_object
    }

################################################################################

# #Main program to run app (Commented because Dockerfile contains commands to run)
# def main():
#     uvicorn.run(
#         app="app:app",
#         host="127.0.0.1",
#         port=8000,
#         reload=True
#         )

# if __name__ == "__main__":
#     main()