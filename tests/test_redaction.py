import json
from src.common import sanitize
from src.telemetry import safe


def test_redaction_idempotent_and_preserves_trace_json():
    text='senha=SEGREDO_FICTICIO_81 e email usuario@example.test CPF 123.456.789-09'
    one=sanitize(text)
    assert 'SEGREDO_FICTICIO_81' not in one and 'usuario@example.test' not in one and '123.456.789-09' not in one
    assert sanitize(one)==one
    packed=json.dumps({'input':one,'owner':'teste'},ensure_ascii=False)
    assert json.loads(safe(packed))['owner']=='teste'
