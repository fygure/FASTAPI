import os
from logger import logger
from fastapi import FastAPI
from opentelemetry import trace, _logs, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider, ConcurrentMultiSpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
###########################################################################
# Manual OpenTelemetry Instrumentation for FastAPI
resource = Resource(attributes={
    "service.name": "fastapi-service",
    "service.version": "1.0.0",
    "service.instance.id": "instance-1",
})
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
    -Find & Replace elastic apm observability with OTLP
    -Metrics are set up but metric instrumentation such as adding counters are required in api logic
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
trace_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace_provider.add_span_processor(span_processor)
trace.set_tracer_provider(trace_provider)

# Define a global tracer object for custom spans
TRACER = trace.get_tracer(f"tracer_{__name__}")

# Set up OTLP Metrics
otlp_metric_exporter = OTLPMetricExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")
)
metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)
meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(meter_provider)

# Define a global meter provider
METRICS = metrics.get_meter(f"meter_{__name__}")

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

#Custom Instruments: must create an instance before calling instrument()
httpx_instrumentor = HTTPXClientInstrumentor()
httpx_instrumentor.instrument()

###########################################################################
# To be used in entry point (app.py)
def mount_telemetry(app: FastAPI):
    logger.addHandler(otel_logging_handler) #Must add logging handler on mount to export to collector
    FastAPIInstrumentor.instrument_app(
        app=app,
        tracer_provider=trace_provider,
        meter_provider=meter_provider
    )

def dismount_telemetry():
    logger_provider.shutdown()
    trace_provider.shutdown()