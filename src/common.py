import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def tokens(text):
    text = unicodedata.normalize('NFKD', text.lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    stop = {'para', 'como', 'qual', 'que', 'uma', 'com', 'por', 'meu', 'minha', 'nao', 'esta', 'dos', 'das'}
    return {w for w in re.findall(r'[a-z0-9]+', text) if len(w) > 2 and w not in stop}


def sanitize(text):
    # Defesa limitada e explícita: somente dados fictícios são aceitos neste protótipo.
    text = re.sub(r'sk-[A-Za-z0-9_-]+', '[SEGREDO]', text)
    text = re.sub(r'mstrl_[A-Za-z0-9_-]+', '[SEGREDO]', text)
    text = re.sub(r'(?i)\b(senha|token|password)\s*[:=]\s*\S+', r'\1=[REMOVIDO]', text)
    text = re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b', '[EMAIL]', text)
    return text
