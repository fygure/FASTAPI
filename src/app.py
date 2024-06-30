import os
from typing import Union
#import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

#Load .env vars
load_dotenv()

#Init FastAPI app
app = FastAPI()

#Pydantic
class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


###########################################################################
# Manual OpenTelemetry Instrumentation for FastAPI
# Set up Tracer
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Auto-instrument FastAPI app
FastAPIInstrumentor.instrument_app(app)

# Define a global tracer object for custom spans
TRACER = trace.get_tracer(__name__)
###########################################################################
#Routes
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/send")
async def send_things(my_object: Item):
    return {
        "status": "ok",
        "received_object": my_object
    }

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

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