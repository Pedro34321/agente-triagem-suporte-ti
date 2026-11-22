import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from src.model import LLM
from src.model import MODEL, PROVIDER
from src.common import ROOT, canonical
from src.telemetry import Telemetry, safe


class Judgment(BaseModel):
    model_config = ConfigDict(extra='forbid')
    aprovado: bool
    nota: str


def judge(entry, output):
    telemetry=Telemetry(ROOT/'.runtime/juiz/traces')
    model=LLM()
    with telemetry.span('chat '+MODEL,{'gen_ai.operation.name':'chat','gen_ai.request.model':MODEL,
                        'gen_ai.provider.name':PROVIDER,'triagem.role':'evaluation_judge'}) as span:
        result,_=model.call('juiz', Judgment, {'entrada': entry, 'saida': output},timeout=90)
        span.set_attribute('gen_ai.usage.input_tokens',model.last_usage['input'])
        span.set_attribute('gen_ai.usage.output_tokens',model.last_usage['output'])
        span.set_attribute('triagem.judgment',canonical(result))
        return result
