"""Nunca inventa rótulos humanos nem concordância. Adota só após validação completa."""
import argparse
import json
import time
from pathlib import Path
from src.common import ROOT
from .juiz import judge


def prepare(round_dir):
    cases=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(round_dir.glob('*.json')) if p.stem not in ('resumo','metricas')]
    cases=[c for c in cases if 'entrada' in c and 'saida' in c]
    # Diversidade: nove saídas reais da Parte 2 mais onze da rodada atual.
    previous=[]
    for path in sorted((ROOT/'logs/parte2').glob('caso_*.json')):
        c=json.loads(path.read_text(encoding='utf-8'))
        previous.append({'id':'parte2_'+path.stem,'entrada':c['entrada'],'saida':c['saida']})
    cases=(previous+cases)[:20]
    if len(cases)<20: raise ValueError('Necessárias vinte saídas reais.')
    packet=[{'id':c['id'],'entrada':c['entrada'],'saida':c['saida']['resultado'],
             'humano':None,'nota_humana':'','revisor_humano':''} for c in cases]
    dest=ROOT/'evals/revisao'
    dest.mkdir(exist_ok=True)
    (dest/'rotulos-humanos.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Revisão humana do juiz — vinte saídas reais','',
           'Rubrica: a resposta permite entender o próximo passo? Aceita classificação/encaminhamento compreensível, pergunta específica ou recusa com alternativa útil.',
           'Responda SIM ou NÃO e escreva uma razão por caso. Informe seu nome como revisor. Não avalie apenas se o JSON está bem formado.',
           'Limiar de adoção previamente declarado: concordância >=90%, com vinte rótulos humanos válidos.','']
    for c in packet:
        lines += [f'## {c["id"]}', 'Entrada: '+c['entrada'],'','Resposta: '+c['saida'],'',
                  'Rótulo humano (SIM/NÃO): ______','Razão: ______','Revisor humano: ______','']
    (dest/'PARA-REVISAO-HUMANA.md').write_text('\n'.join(lines),encoding='utf-8')


def main():
    p=argparse.ArgumentParser();p.add_argument('--preparar');p.add_argument('--avaliar',action='store_true');p.add_argument('--consolidar',action='store_true');p.add_argument('--intervalo',type=float,default=35);a=p.parse_args()
    if a.preparar: prepare(Path(a.preparar));return
    dest=ROOT/'evals/revisao'
    packet=json.loads((dest/'rotulos-humanos.json').read_text(encoding='utf-8'))
    result=[]
    for index,c in enumerate(packet if not a.consolidar else []):
        if index:time.sleep(max(0,a.intervalo))
        try:
            j=judge(c['entrada'],c['saida'])
            result.append(dict(c,juiz=j['aprovado'],nota_juiz=j['nota']))
        except Exception as exc:
            result.append(dict(c,juiz=None,nota_juiz='',erro=type(exc).__name__))
        print(c['id'],flush=True)
        (dest/'predicoes-parciais.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.consolidar:
        predictions={c['id']:c for c in json.loads((dest/'predicoes-parciais.json').read_text(encoding='utf-8'))}
        result=[dict(c,juiz=predictions[c['id']]['juiz'],nota_juiz=predictions[c['id']]['nota_juiz']) for c in packet]
    human_ok=all(isinstance(c['humano'],bool) and c['nota_humana'].strip() and c['revisor_humano'].strip() for c in result)
    judge_ok=all(isinstance(c['juiz'],bool) for c in result)
    ready=human_ok and judge_ok
    matrix={'humano_sim_juiz_sim':0,'humano_sim_juiz_nao':0,'humano_nao_juiz_sim':0,'humano_nao_juiz_nao':0} if ready else None
    disagreements=[]
    if ready:
        for c in result:
            matrix['humano_'+('sim' if c['humano'] else 'nao')+'_juiz_'+('sim' if c['juiz'] else 'nao')]+=1
            if c['humano']!=c['juiz']:
                disagreements.append(dict(c,classificacao='PENDENTE: defeito do juiz, da rubrica ou do rótulo humano'))
    agreement=sum(c['humano']==c['juiz'] for c in result)/20 if ready else None
    report={'rubrica':'1.0.0','limiar':0.9,'revisao_humana_completa':human_ok,'matriz':matrix,
            'predicoes_completas':judge_ok,'concordancia':agreement,'adotado':bool(ready and agreement>=0.9 and not disagreements),
            'desacordos':disagreements,'casos':result,
            'lacuna':None if human_ok else 'Vinte rótulos, razões e identificação de revisor humano ainda não fornecidos.'}
    (dest/'validacao-juiz.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': main()
