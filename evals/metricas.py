"""Métricas por versão, calculadas dos spans exportados, sem misturar rodadas."""
import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def metrics(directory):
    spans=[]
    for p in Path(directory).glob('traces/**/*.jsonl'):
        spans += [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
    groups=defaultdict(list)
    for s in spans:
        if s['name']=='invoke_agent triagem-ti':
            groups[s['attributes']['triagem.system.version']].append(s)
    report={}
    for version,roots in groups.items():
        times=sorted((datetime.fromisoformat(s['end_time'])-datetime.fromisoformat(s['start_time'])).total_seconds() for s in roots)
        ids={s['context']['trace_id'] for s in roots}
        children=[s for s in spans if s['context']['trace_id'] in ids]
        tools=defaultdict(lambda:{'chamadas':0,'erros':0})
        chats=[s for s in children if s['name'].startswith('chat ')]
        for s in children:
            if s['name'].startswith('execute_tool '):
                t=tools[s['attributes']['gen_ai.tool.name']];t['chamadas']+=1
                t['erros']+=bool(s['attributes'].get('error.type'))
        costs={}
        for id in ids:
            calls=[s for s in chats if s['context']['trace_id']==id]
            complete=all('triagem.estimated_cost_usd' in s['attributes'] for s in calls)
            costs[id]=sum(s['attributes']['triagem.estimated_cost_usd'] for s in calls) if complete else None
        known=[c for c in costs.values() if c is not None]
        good=sum(s['attributes'].get('triagem.quality.good') is True for s in roots)
        n=len(roots);allowed=n*0.1;bad=n-good
        report[version]={'execucoes':n,'p50_s':times[math.ceil(n*0.5)-1],'p95_s':times[math.ceil(n*0.95)-1],
            'custo_estimado_usd_total_conhecido':sum(known),'custo_estimado_usd_por_execucao':sum(known)/n if len(known)==n else None,
            'custo_limite_inferior_por_execucao':sum(known)/n,'execucoes_com_custo_conhecido':len(known),
            'lacuna_custo':'API sem usage não permite inferir custo zero' if len(known)!=n else None,
            'custos_individuais_usd':costs,'chamadas_modelo':len(chats),
            'tokens_input':sum(s['attributes'].get('gen_ai.usage.input_tokens',0) for s in chats),
            'tokens_output':sum(s['attributes'].get('gen_ai.usage.output_tokens',0) for s in chats),
            'motivos':dict(Counter(s['attributes'].get('triagem.termination_reason') for s in roots)),
            'ferramentas':{k:dict(v,taxa_erro=v['erros']/v['chamadas']) for k,v in tools.items()},
            'slo':{'validos':n,'bons':good,'sli':good/n,'alvo':0.9,'janela':'7 dias',
                   'orçamento_erros':allowed,'erros_observados':bad,'consumo_orcamento':bad/allowed,
                   'violado':good/n<0.9,'escopo':'amostra sintética/desenvolvimento desta rodada, não produção'}}
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('rodada');a=p.parse_args()
    report=metrics(a.rodada)
    (Path(a.rodada)/'metricas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
