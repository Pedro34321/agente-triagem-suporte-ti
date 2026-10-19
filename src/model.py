import os
from dotenv import load_dotenv
from openai import OpenAI
from .common import ROOT, canonical, digest

load_dotenv(ROOT / '.env.local')
load_dotenv(ROOT / '.env')
PROVIDER = os.getenv('LLM_PROVIDER') or 'mistral'
MODEL = os.getenv('LLM_MODEL') or ('ministral-3b-2512' if PROVIDER == 'mistral' else 'gpt-4.1-mini-2025-04-14')


def prompt(name):
    return (ROOT / 'src/prompts' / (name + '.txt')).read_text(encoding='utf-8')


def prompt_versions():
    return {p.name: digest(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'src/prompts').glob('*.txt'))}


class LLM:
    def __init__(self):
        self.client = None

    def call(self, name, schema, data, timeout=30, override=None):
        if self.client is None:
            if PROVIDER not in ('mistral', 'openai'):
                raise ValueError('Provedor deve ser mistral ou openai.')
            self.client = OpenAI(api_key=os.getenv('MISTRAL_API_KEY' if PROVIDER == 'mistral' else 'OPENAI_API_KEY'),
                                 base_url='https://api.mistral.ai/v1' if PROVIDER == 'mistral' else 'https://api.openai.com/v1',
                                 max_retries=0, timeout=30)
        messages = [{'role': 'system', 'content': (override if override is not None else prompt(name)) + '\n' + prompt('procedural')},
                    {'role': 'user', 'content': canonical(data)}]
        if PROVIDER == 'mistral':
            response = self.client.chat.completions.create(
                model=MODEL, messages=messages, temperature=0, max_tokens=1200,
                response_format={'type': 'json_schema', 'json_schema': {'name': schema.__name__, 'schema': schema.model_json_schema(), 'strict': True}},
                timeout=max(1, min(timeout, 30)),
            )
            parsed = schema.model_validate_json(response.choices[0].message.content)
            return parsed.model_dump(), response.usage.total_tokens
        response = self.client.responses.parse(
            model=MODEL, store=False, temperature=0,
            input=messages,
            text_format=schema, max_output_tokens=1200, timeout=max(1, min(timeout, 30)),
        )
        if response.output_parsed is None:
            raise ValueError('resposta_sem_objeto')
        return response.output_parsed.model_dump(), response.usage.total_tokens
