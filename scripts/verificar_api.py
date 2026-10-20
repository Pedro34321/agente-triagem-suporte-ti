"""Diagnóstico sem imprimir chave, cabeçalhos, conteúdo do erro ou relato."""
from src.model import LLM
from src.contracts import Interpretation

try:
    result, tokens = LLM().call('interpretar', Interpretation, {'relato': 'Senha do email incorreta.'})
    print({'ok': True, 'tokens': tokens})
except Exception as exc:
    body = getattr(exc, 'body', {})
    error = body.get('error', body) if isinstance(body, dict) else {}
    print({'ok': False, 'tipo': type(exc).__name__, 'status': getattr(exc, 'status_code', None),
           'codigo': error.get('code'), 'classe': error.get('type')})
