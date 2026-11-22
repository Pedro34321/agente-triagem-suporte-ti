"""Nunca inventa rótulos humanos nem concordância. Adota só após validação completa."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from src.common import ROOT
from .juiz import judge


def case_hash(case):
    return hashlib.sha256((case['entrada']+'\n'+case['saida']).encode('utf-8')).hexdigest()


def consolidate(packet, predictions, reviews=None, threshold=0.9, rubric_version='1.0.0'):
    """Consolida evidências existentes; análises antigas não valem para outro caso."""
    ids=[c['id'] for c in packet]
    if len(ids)!=20 or len(set(ids))!=20:
        raise ValueError('São necessários vinte casos únicos.')
    if len(predictions)!=20 or {c['id'] for c in predictions}!=set(ids):
        raise ValueError('Predições devem corresponder aos vinte casos.')
    predicted={c['id']:c for c in predictions}
    for c in packet:
        if case_hash(c)!=case_hash(predicted[c['id']]):
            raise ValueError('Predição pertence a outra entrada/saída: '+c['id'])
    result=[dict(c,juiz=predicted[c['id']]['juiz'],nota_juiz=predicted[c['id']]['nota_juiz']) for c in packet]
    for c in result:
        source=predicted[c['id']]
        c.update({k:source[k] for k in ('juiz_bruto','nota_juiz_bruto','metodo','regra') if k in source})
    human_ok=all(isinstance(c['humano'],bool) and c['nota_humana'].strip() and c['revisor_humano'].strip() for c in result)
    judge_ok=all(isinstance(c['juiz'],bool) for c in result)
    ready=human_ok and judge_ok
    matrix={'humano_sim_juiz_sim':0,'humano_sim_juiz_nao':0,'humano_nao_juiz_sim':0,'humano_nao_juiz_nao':0} if ready else None
    reviews=reviews or []
    reviewed={r['id']:r for r in reviews}
    if len(reviewed)!=len(reviews):raise ValueError('Análises duplicadas.')
    disagreements=[]
    if ready:
        for c in result:
            matrix['humano_'+('sim' if c['humano'] else 'nao')+'_juiz_'+('sim' if c['juiz'] else 'nao')]+=1
            if c['humano']!=c['juiz']:
                item=dict(c,classificacao='PENDENTE: defeito do juiz, da rubrica ou do rótulo humano')
                if c['id'] in reviewed:
                    r=reviewed[c['id']]
                    if (r.get('caso_sha256')!=case_hash(c) or r.get('humano') is not c['humano']
                            or r.get('juiz') is not c['juiz']):
                        raise ValueError('Análise desatualizada: '+c['id'])
                    if (r.get('classificacao') not in ('defeito do juiz','defeito da rubrica','defeito do rótulo humano')
                            or not r.get('analise','').strip() or not r.get('analista','').strip()):
                        raise ValueError('Análise incompleta: '+c['id'])
                    item.update({k:r[k] for k in ('classificacao','analise','analista','caso_sha256')})
                disagreements.append(item)
    if set(reviewed)-{c['id'] for c in disagreements}:
        raise ValueError('Análise sem desacordo correspondente.')
    agreement=sum(c['humano']==c['juiz'] for c in result)/20 if ready else None
    analyzed=ready and all(not c['classificacao'].startswith('PENDENTE') for c in disagreements)
    return {'rubrica':rubric_version,'limiar':threshold,'revisao_humana_completa':human_ok,'matriz':matrix,
            'predicoes_completas':judge_ok,'concordancia':agreement,
            'desacordos_analisados':analyzed,'adotado':bool(ready and agreement>=threshold and analyzed),
            'desacordos':disagreements,'casos':result,
            'lacuna':None if human_ok else 'Vinte rótulos, razões e identificação de revisor humano ainda não fornecidos.'}


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
    p=argparse.ArgumentParser();p.add_argument('--preparar');p.add_argument('--avaliar',action='store_true');p.add_argument('--consolidar',action='store_true');p.add_argument('--intervalo',type=float,default=3);p.add_argument('--destino');a=p.parse_args()
    if a.preparar: prepare(Path(a.preparar));return
    policy=json.loads((ROOT/'evals/politica.json').read_text(encoding='utf-8'))
    dest=Path(a.destino) if a.destino else (ROOT/policy.get('validacao_juiz','evals/revisao/validacao-juiz.json')).parent
    dest.mkdir(parents=True,exist_ok=True)
    packet=json.loads((ROOT/'evals/revisao/rotulos-humanos.json').read_text(encoding='utf-8'))
    if not a.consolidar and (dest/'predicoes-parciais.json').exists():
        p.error('Esta coleta já existe. Use --destino NOVA_PASTA para preservar o histórico.')
    from src.model import PROVIDER, prompt_versions
    from .juiz import JUDGE_MODEL
    metadata_path=dest/'coleta.json'
    if a.consolidar:
        previous_path=dest/'validacao-juiz.json'
        previous=json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
        metadata=(json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.exists()
                  else {k:previous[k] for k in ('modelo','provedor','prompt_hash','rubrica') if k in previous})
        if metadata.get('rubrica',policy['rubrica_version'])!=policy['rubrica_version']:
            p.error('Rubrica da coleta difere da política atual. Preserve o histórico e use uma nova pasta.')
    else:
        metadata={'modelo':JUDGE_MODEL,'provedor':PROVIDER,'prompt_hash':prompt_versions()['juiz.txt'],
                  'rubrica':policy['rubrica_version'],'modo':'hibrido'}
        metadata_path.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    result=[]
    for index,c in enumerate(packet if not a.consolidar else []):
        if index:time.sleep(max(0,a.intervalo))
        try:
            j=judge(c['entrada'],c['saida'])
            result.append(dict(c,juiz=j['aprovado'],nota_juiz=j['nota'],metodo=j.get('metodo','llm'),regra=j.get('regra')))
        except Exception as exc:
            result.append(dict(c,juiz=None,nota_juiz='',erro=type(exc).__name__))
        print(c['id'],flush=True)
        (dest/'predicoes-parciais.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.consolidar:
        result=json.loads((dest/'predicoes-parciais.json').read_text(encoding='utf-8'))
    review_path=dest/'analise-desacordos.json'
    reviews=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else []
    report=consolidate(packet,result,reviews,policy['limiar_adocao_juiz'],policy['rubrica_version'])
    report.update(metadata,proveniencia_rotulos='evals/revisao/PROVENIENCIA-REVISAO.md')
    (dest/'validacao-juiz.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': main()
