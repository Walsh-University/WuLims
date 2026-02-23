import os
from collections.abc import Sequence
from typing import Any

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanContext, TraceFlags
from audit.middleware import get_request_id

_otel_configured = False


def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _parse_otel_headers(raw: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    for part in raw.split(","):
        item = part.strip()
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            headers[key] = value
    return headers


def _resolve_service_name() -> str:
    return os.getenv("OTEL_SERVICE_NAME") or os.getenv("SERVICE_NAME") or "wulims"


def _build_trace_exporter() -> OTLPSpanExporter | None:
    endpoint = (
        os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or ""
    ).strip()
    if not endpoint:
        return None

    headers = _parse_otel_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS", ""))
    return OTLPSpanExporter(
        endpoint=endpoint,
        insecure=env_bool("OTEL_EXPORTER_OTLP_INSECURE", "1"),
        headers=headers or None,
        timeout=float(os.getenv("OTEL_EXPORTER_OTLP_TIMEOUT", "10")),
    )


def configure_opentelemetry() -> None:
    global _otel_configured

    if _otel_configured:
        return
    _otel_configured = True

    if not env_bool("OTEL_ENABLED", "1"):
        return

    current_provider = trace.get_tracer_provider()
    if not isinstance(current_provider, TracerProvider):
        exporter = _build_trace_exporter()
        if exporter is not None:
            resource = Resource.create(
                {
                    "service.name": _resolve_service_name(),
                    "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "wulims"),
                    "service.version": os.getenv("OTEL_SERVICE_VERSION", "0.1.0"),
                    "deployment.environment": os.getenv("OTEL_ENVIRONMENT", "production"),
                }
            )
            provider = TracerProvider(resource=resource)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)

    instrumentor = DjangoInstrumentor()
    if not instrumentor.is_instrumented_by_opentelemetry:
        instrumentor.instrument()


def add_otel_trace_context(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    span = trace.get_current_span()
    if span is None:
        return event_dict

    context = span.get_span_context()
    if context is None or not isinstance(context, SpanContext):
        return event_dict
    if context.trace_id == 0 or context.span_id == 0:
        return event_dict

    event_dict["trace_id"] = f"{context.trace_id:032x}"
    event_dict["span_id"] = f"{context.span_id:016x}"
    event_dict["trace_flags"] = int(TraceFlags(context.trace_flags))
    return event_dict


def structlog_pre_chain() -> Sequence[Any]:
    return (
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_otel_trace_context,
    )


def add_request_id(logger, method_name, event_dict):
    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def configure_structlog() -> None:
    processors = list(structlog_pre_chain())

    processors.append(add_request_id)

    processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def build_logging_config(log_level: str, json_logs: bool = True) -> dict[str, Any]:
    render_processor: Any
    if json_logs:
        render_processor = structlog.processors.JSONRenderer()
    else:
        render_processor = structlog.dev.ConsoleRenderer(colors=False)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structlog": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": render_processor,
                "foreign_pre_chain": list(structlog_pre_chain()),
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "structlog",
            }
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "django.server": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "django.security.DisallowedHost": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
            "gunicorn": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "gunicorn.error": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "gunicorn.access": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
        },
    }
