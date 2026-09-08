"""OpenTelemetry observability provider."""

import logging
import os

logger = logging.getLogger(__name__)


def init_otel():
    # Only init if OTLP endpoint is configured or explicit enable
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    otel_enabled = os.getenv("OTEL_ENABLED", "")
    if not otlp_endpoint and otel_enabled.lower() not in ("true", "1", "yes"):
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
    except ImportError:
        logger.warning("opentelemetry packages not installed, skipping OTel init")
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "{{ cookiecutter.project_slug }}")
    resource = Resource.create({"service.name": service_name})

    provider = TracerProvider(resource=resource)

    # OTLP exporter (HTTP)
    endpoint = otlp_endpoint or "http://localhost:4318/v1/traces"
    headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    # headers format: "key1=value1,key2=value2"
    exporter_kwargs = {"endpoint": endpoint}
    if headers:
        exporter_kwargs["headers"] = dict(
            h.split("=", 1) for h in headers.split(",") if "=" in h
        )

    try:
        otlp_exporter = OTLPSpanExporter(**exporter_kwargs)
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)

        # Instrument libraries
        DjangoInstrumentor().instrument()
        try:
            PsycopgInstrumentor().instrument()
        except Exception:
            pass
        try:
            CeleryInstrumentor().instrument()
        except Exception:
            pass
        try:
            RedisInstrumentor().instrument()
        except Exception:
            pass

        logger.info("OpenTelemetry initialized (service=%s endpoint=%s)", service_name, endpoint)
    except Exception as exc:  # pragma: no cover
        logger.warning("OpenTelemetry init failed: %s", exc)
