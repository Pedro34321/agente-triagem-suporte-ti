"""Medições locais reais, sem chamadas ao modelo e sem alegar qualidade do LLM."""
import json
import operator
import subprocess
from datetime import datetime, timezone
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from src.common import ROOT
from src.knowledge import search, records
from src.contracts import Output, Interpretation, Decision, DraftDecision


def reducer_demo():
    class Plain(TypedDict):
        events: list[str]
    class Accum(TypedDict):
        events: Annotated[list[str], operator.add]
    results = {}
    for name, schema in [('sem_reducer', Plain), ('com_reducer', Accum)]:
        builder = StateGraph(schema)
        builder.add_node('a', lambda s: {'events': ['a']})
        builder.add_node('b', lambda s: {'events': ['b']})
        builder.add_edge(START, 'a')
        builder.add_edge('a', 'b')
        builder.add_edge('b', END)
        results[name] = builder.compile().invoke({'events': []})
    # No LangGraph atual, escrita concorrente sem reducer levanta erro; não omitir isso.
    builder = StateGraph(Plain)
    builder.add_node('a', lambda s: {'events': ['a']})
    builder.add_node('b', lambda s: {'events': ['b']})
    builder.add_edge(START, 'a')
    builder.add_edge(START, 'b')
    builder.add_edge('a', END)
    builder.add_edge('b', END)
    try:
        builder.compile().invoke({'events': []})
    except Exception as exc:
        results['paralelo_sem_reducer'] = type(exc).__name__
    return results


def main():
    questions = json.loads((ROOT / 'dados/perguntas_rag.json').read_text(encoding='utf-8'))
    results = []
    for q in questions:
        if q['forma'] == 'textual':
            found = search(q['pergunta'], q['topic'])
        else:
            found, _ = records({'asset': q.get('asset'), 'location': q.get('location'), 'topic': 'rede'})
        correct = (not found if q['fonte'] is None else any(s['id'] == q['fonte'] and q['trecho'] in s['texto'] for s in found))
        results.append({'id': q['id'], 'fontes': [s['id'] for s in found], 'acerto': correct})
    data = {'tipo': 'avaliacao_local_sem_modelo', 'data': datetime.now(timezone.utc).isoformat(),
            'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'rag': results, 'acertos': sum(r['acerto'] for r in results), 'total': len(results),
            'revogado_sem_filtro': [s['id'] for s in search('configurar VPN', 'vpn', True)],
            'revogado_com_filtro': [s['id'] for s in search('configurar VPN', 'vpn')], 'reducers': reducer_demo()}
    destination = ROOT / 'logs/parte2'
    destination.mkdir(exist_ok=True)
    (destination / 'avaliacao-local.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    for name, schema in [('saida', Output), ('interpretacao', Interpretation), ('decisao', Decision), ('rascunho', DraftDecision)]:
        (ROOT / 'docs' / f'schema-{name}.json').write_text(json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
