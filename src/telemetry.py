"""OpenTelemetry real, exportação JSONL local consultável por trace_id."""
import json
import threading
import functools
from contextlib import contextmanager
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode, SpanKind
from .common import canonical, sanitize
from .version import VERSION


def safe(value):
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items() if k.lower() not in ('api_key', 'authorization', 'token', 'credential')}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return sanitize(value) if isinstance(value, str) else value


class JsonExporter(SpanExporter):
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.failed = False

    def export(self, spans):
        try:
            with self.lock:
                for span in spans:
                    path = self.directory / f'{span.context.trace_id:032x}.jsonl'
                    data = json.loads(span.to_json())
                    # Exceções são registradas por tipo, nunca str(exc) ou stack com dados.
                    with path.open('a', encoding='utf-8') as f:
                        f.write(canonical(safe(data)) + '\n')
            return SpanExportResult.SUCCESS
        except OSError:
            self.failed = True
            return SpanExportResult.FAILURE


class Telemetry:
    def __init__(self, directory):
        self.exporter = JsonExporter(directory)
        self.provider = TracerProvider(resource=Resource.create({'service.name': 'triagem-ti', 'service.version': VERSION}))
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = self.provider.get_tracer('triagem-ti', VERSION)

    @contextmanager
    def span(self, name, attributes=None, kind=SpanKind.INTERNAL):
        with self.tracer.start_as_current_span(name, attributes=attributes or {}, kind=kind,
                                              record_exception=False, set_status_on_exception=False) as span:
            try:
                yield span
            except Exception as exc:
                span.set_attribute('error.type', type(exc).__name__)
                span.set_status(Status(StatusCode.ERROR))
                raise

    def tool(self, name, arguments, fn):
        with self.span('execute_tool ' + name, {'gen_ai.operation.name': 'execute_tool',
                        'gen_ai.tool.name': name, 'gen_ai.tool.type': 'function',
                        'gen_ai.tool.call.arguments': canonical(safe(arguments))}) as span:
            result = fn()
            span.set_attribute('gen_ai.tool.call.result', canonical(safe(result)))
            if name == 'consultar_cadastro' and result[1]:
                span.set_attribute('error.type', 'registro_nao_encontrado')
                span.set_status(Status(StatusCode.ERROR))
            return result

    def ensure_available(self):
        with self.span('audit_preflight'):
            pass
        if self.exporter.failed:
            raise PermissionError('Trace indisponível: escrita bloqueada.')


def event(name, data):
    trace.get_current_span().add_event(name, {'data': canonical(safe(data))})


def observed(fn):
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        from .model import MODEL, PROVIDER, prompt_versions
        with self.telemetry.span('invoke_agent triagem-ti', {
            'gen_ai.operation.name': 'invoke_agent', 'gen_ai.agent.name': 'triagem-ti',
            'gen_ai.agent.version': VERSION, 'gen_ai.provider.name': PROVIDER,
            'gen_ai.request.model': MODEL, 'triagem.system.version': VERSION,
            'triagem.operation': fn.__name__, 'triagem.input': canonical(safe({'args': args, 'kwargs': kwargs})),
            'triagem.prompts': canonical(prompt_versions()), 'triagem.environment': 'local-ficticio'
        }) as span:
            self.last_trace_id = f'{span.get_span_context().trace_id:032x}'
            try:
                result = fn(self, *args, **kwargs)
            except Exception:
                span.set_attribute('triagem.termination_reason', 'erro')
                span.set_attribute('triagem.quality.good', False)
                raise
            reason = result['motivo_termino']
            good = reason in {'registrado','informativo','base_insuficiente','incompleto','ambiguo','fora_escopo','aguardando_aprovacao','rejeitado'}
            span.set_attribute('triagem.termination_reason', reason)
            span.set_attribute('triagem.quality.good', good)
            span.set_attribute('gen_ai.conversation.id', result['thread_id'])
            span.set_attribute('triagem.output', canonical(safe(result)))
            return result
    return wrapped
