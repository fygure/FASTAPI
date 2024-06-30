import os
from logger import logger
from fastapi import FastAPI
from opentelemetry import trace, _logs
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider, ConcurrentMultiSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

###########################################################################
# Manual OpenTelemetry Instrumentation for FastAPI

#TODO
"""_Create Package_
Configurations to ingest from api owners:
    -Exporter endpoints for Tracer, Log, Metrics
    -Logger object needed in this package to mount the OTLP log exporter
    -List of instruments outside of bootstrap (feedback loop)
    -Service to the bootstrappable instruments only for now
    -Service to the automatic instrumentation for now
    -Manual instrumentation will require work within the code
    -Perhaps create decorators for api routes that can inject manual tracing/spans?
"""

#V1 (WORKS)
#Set up OTLP Tracer
# trace.set_tracer_provider(TracerProvider())
# otlp_exporter = OTLPSpanExporter(
#     endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
# )
# span_processor = BatchSpanProcessor(otlp_exporter)
# trace.get_tracer_provider().add_span_processor(span_processor)

#V2
trace_provider = TracerProvider()
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace_provider.add_span_processor(span_processor)
trace.set_tracer_provider(trace_provider)

#TODO Set up OTLP Metrics

# Set up OTLP Logging
logger_provider = LoggerProvider() #TODO: resource= on prod
handler = LoggingHandler(logger_provider=logger_provider)
otlp_log_exporter = OTLPLogExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"),
)
log_processor = BatchLogRecordProcessor(otlp_log_exporter)
logger_provider.add_log_record_processor(log_processor)
_logs.set_logger_provider(logger_provider)
otel_logging_handler = LoggingHandler(logger_provider=logger_provider)


# Define a global tracer object for custom spans
TRACER = trace.get_tracer(__name__)
###########################################################################
# To be used in entry point (app.py)
def mount_telemetry(app: FastAPI):
    logger.addHandler(otel_logging_handler) #Must add logging handler on mount to export to collector
    FastAPIInstrumentor.instrument_app(
        app=app,
        tracer_provider=trace_provider
    )

def dismount_telemetry():
    logger_provider.shutdown()
    trace_provider.shutdown()