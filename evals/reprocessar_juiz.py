"""Reaplica regra explícita às previsões reais, preservando votos brutos e origem."""
import argparse
import json
from pathlib import Path
from src.common import ROOT,digest
from .calibrar_juiz import consolidate
from .regra_juiz import fixed_message_judgment


def transform(case):
    if not isinstance(case['juiz'],bool):raise ValueError('Predição LLM ausente.')
    result=dict(case,juiz_bruto=case['juiz'],nota_juiz_bruto=case['nota_juiz'],metodo='llm')
    fixed=fixed_message_judgment(case['saida'])
    if fixed:
        result.update(juiz=fixed['aprovado'],nota_juiz=fixed['nota'],metodo=fixed['metodo'],regra=fixed['regra'])
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('origem');p.add_argument('destino');a=p.parse_args()
    source=Path(a.origem);dest=Path(a.destino)
    if (dest/'predicoes-parciais.json').exists():raise SystemExit('Destino já contém previsões; não sobrescrever histórico.')
    read=lambda path:json.loads(path.read_text(encoding='utf-8'))
    original=read(source/'predicoes-parciais.json')
    raw_report=read(source/'validacao-juiz.json')
    policy=read(ROOT/'evals/politica.json')
    packet=read(ROOT/'evals/revisao/rotulos-humanos.json')
    transformed=[transform(c) for c in original]
    changed=[c['id'] for c in transformed if c['juiz']!=c['juiz_bruto']]
    disagreed={c['id'] for c in transformed if c['juiz']!=c['humano']}
    reviews=[c for c in read(source/'analise-desacordos.json') if c['id'] in disagreed]
    report=consolidate(packet,transformed,reviews,policy['limiar_adocao_juiz'],policy['rubrica_version'])
    metadata={'modelo':raw_report['modelo'],'provedor':raw_report['provedor'],'prompt_hash':raw_report['prompt_hash'],
              'rubrica':policy['rubrica_version'],'modo':'hibrido','origem_predicoes_llm':(source/'predicoes-parciais.json').as_posix(),
              'sha256_predicoes_origem':digest(original),'concordancia_llm_isolado':raw_report['concordancia'],
              'sha256_codigo_regra':digest((ROOT/'evals/regra_juiz.py').read_text(encoding='utf-8')),
              'regras_aplicadas':sum(c['metodo']=='deterministico' for c in transformed),'votos_alterados_pela_regra':changed,
              'novas_chamadas_api':0,'predicoes_llm_reais_reutilizadas':len(original),
              'proveniencia_rotulos':'evals/revisao/PROVENIENCIA-REVISAO.md'}
    report.update(metadata)
    dest.mkdir(parents=True,exist_ok=True)
    for name,data in [('predicoes-parciais.json',transformed),('validacao-juiz.json',report),
                      ('analise-desacordos.json',reviews),('coleta.json',metadata)]:
        (dest/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'llm_isolado':raw_report['concordancia'],'hibrido':report['concordancia'],
           'matriz':report['matriz'],'adotado':report['adotado'],'votos_corrigidos':changed})


if __name__=='__main__':main()
