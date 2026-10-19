import json
import sqlite3
from .common import ROOT, tokens, canonical


def corpus():
    return json.loads((ROOT / 'dados/corpus.json').read_text(encoding='utf-8'))


def search(query, topic=None, include_revoked=False):
    """Busca textual por termos + filtro de assunto; documentos curtos inteiros."""
    query_tokens = tokens(query)
    matches = []
    for doc in corpus():
        if not doc['vigente'] and not include_revoked:
            continue
        overlap = query_tokens & tokens(doc['termos'] + ' ' + doc['texto'])
        if overlap and (topic is None or topic in doc['assuntos']):
            matches.append((len(overlap), doc))
    return [{'id': d['id'], 'texto': d['texto'], 'origem': 'dados/corpus.json',
             'versao': d['versao']} for _, d in sorted(matches, key=lambda x: (-x[0], x[1]['id']))]


def records(info):
    """Cadastros simulados da Parte 1 são fonte somente leitura."""
    sources, errors = [], []
    with sqlite3.connect(f'file:{(ROOT / "dados/suporte.db").as_posix()}?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        if info['asset']:
            row = conn.execute('SELECT patrimonio,tipo,status,localizacao FROM equipamentos WHERE patrimonio=?', (info['asset'],)).fetchone()
            if row:
                sources.append({'id': 'equipamento:' + info['asset'], 'texto': canonical(dict(row)), 'origem': 'cadastro simulado', 'versao': 'parte1'})
            else:
                errors.append({'tipo': 'registro_nao_encontrado', 'patrimonio': info['asset'], 'recuperavel': True})
        if info['topic'] in ('rede', 'software'):
            for row in conn.execute("SELECT id,titulo,categoria,localizacao,usuarios_afetados FROM incidentes WHERE status='Ativo'"):
                # Localização explícita é obrigatória; senha individual nunca entra aqui.
                if info['location'] and row['localizacao'].casefold() == info['location'].casefold():
                    sources.append({'id': 'incidente:' + str(row['id']), 'texto': canonical(dict(row)), 'origem': 'cadastro simulado', 'versao': 'parte1'})
    return sources, errors
