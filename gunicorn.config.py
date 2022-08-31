import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    resource = Resource.create(attributes={
        "service.name": "api-service"
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT'))
    )
    trace.get_tracer_provider().add_span_processor(span_processor)


DJANGO_SETTINGS_MODULE= dj_ecommerce.settings  OTEL_RESOURCE_ATTRIBUTES=service.name=DjangoApp
OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317" opentelemetry-instrument gunicorn dj_ecommerce.wsgi -c gunicorn.config.py --workers 2 --threads 2 --reload