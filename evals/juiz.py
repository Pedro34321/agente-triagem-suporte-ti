import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from src.model import LLM


class Judgment(BaseModel):
    model_config = ConfigDict(extra='forbid')
    aprovado: bool
    nota: str


def judge(entry, output):
    return LLM().call('juiz', Judgment, {'entrada': entry, 'saida': output})[0]
