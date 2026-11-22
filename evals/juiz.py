import json
import os
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from src.model import LLM
from src.model import MODEL, PROVIDER
from src.common import ROOT, canonical
from src.telemetry import Telemetry, safe
from .regra_juiz import fixed_message_judgment

JUDGE_MODEL=os.getenv('JUDGE_MODEL') or MODEL


class Judgment(BaseModel):
    model_config = ConfigDict(extra='forbid')
    aprovado: bool
    nota: str


def judge(entry, output):
    telemetry=Telemetry(ROOT/'.runtime/juiz/traces')
    fixed=fixed_message_judgment(output)
    if fixed is not None:
        with telemetry.span('evaluate_rule '+fixed['regra'],{'triagem.role':'evaluation_judge',
                            'triagem.judgment':canonical(fixed)}):
            return fixed
    model=LLM(model=JUDGE_MODEL)
    with telemetry.span('chat '+JUDGE_MODEL,{'gen_ai.operation.name':'chat','gen_ai.request.model':JUDGE_MODEL,
                        'gen_ai.provider.name':PROVIDER,'triagem.role':'evaluation_judge'}) as span:
        result,_=model.call('juiz', Judgment, {'entrada': entry, 'saida': output},timeout=90)
        span.set_attribute('gen_ai.usage.input_tokens',model.last_usage['input'])
        span.set_attribute('gen_ai.usage.output_tokens',model.last_usage['output'])
        span.set_attribute('triagem.judgment',canonical(result))
        return result
