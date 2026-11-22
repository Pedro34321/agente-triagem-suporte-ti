"""Invoca a MESMA CLI do README em subprocessos, com bancos isolados por caso."""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from src.common import ROOT, digest
from src.version import VERSION


def db_count(runtime):
    with sqlite3.connect(runtime/'memoria.sqlite') as db:
        return db.execute('SELECT count(*) FROM triagens').fetchone()[0]


def command(args, runtime):
    env = dict(os.environ, TRIAGEM_RUNTIME=str(runtime), PYTHONIOENCODING='utf-8')
    p = subprocess.run([sys.executable,'-m','src.main',*args],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',timeout=150)
    if p.returncode:
        return {'cli_error':True, 'motivo_termino':'erro_cli','suficiente':False,'registro_id':None}
    return json.loads(p.stdout)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--versao',required=True)
    p.add_argument('--rodada',required=True)
    args=p.parse_args()
    if args.versao!=VERSION:
        p.error('Versão deve coincidir com src/version.py, não é rótulo arbitrário.')
    if not args.rodada.replace('-','').replace('_','').isalnum():
        p.error('Nome de rodada inválido.')
    dest=ROOT/'evals/resultados'/args.rodada
    dest.mkdir(parents=True,exist_ok=False)
    dataset=json.loads((ROOT/'evals/dataset.json').read_text(encoding='utf-8'))
    results=[]
    for index,case in enumerate(dataset):
        runtime=ROOT/'.runtime/evals'/args.rodada/case['id']
        start=time.monotonic()
        initial=command(['iniciar',case['entrada'],'--usuario','avaliacao','--caso',case['id']],runtime)
        before=db_count(runtime)
        final=initial
        again=None
        if initial['motivo_termino']=='aguardando_aprovacao':
            response=['retomar',initial['thread_id'],'aprovar']
            if case['esperado'].get('editar'):
                team='Infraestrutura' if initial['encaminhamento']!='Infraestrutura' else 'Suporte N2'
                response=['retomar',initial['thread_id'],'editar','--equipe',team]
            final=command(response,runtime)
            again=command(['retomar',initial['thread_id'],'aprovar'],runtime)
        after=db_count(runtime)
        checks={}
        expected=case['esperado']
        for key in ('categoria','prioridade','suficiente'):
            if key in expected: checks[key]=final.get(key)==expected[key]
        if expected.get('perguntas'): checks['perguntas']=bool(final.get('perguntas'))
        if expected.get('fonte'): checks['fonte']=any(c['id']==expected['fonte'] for c in final.get('fontes',[]))
        checks['resultado_mundo']=(after==1 and final.get('registro_id') is not None) if expected['registro'] else (after==0 and final.get('registro_id') is None)
        checks['pausa_antes_escrita']=before==0
        if expected['registro']:
            checks['pausa']=initial['motivo_termino']=='aguardando_aprovacao'
            checks['idempotencia']=bool(again and again.get('ja_existia') and again.get('registro_id')==final.get('registro_id') and after==1)
        if expected.get('editar'):
            checks['edicao']=initial.get('encaminhamento')!=final.get('encaminhamento')
        spans=[]
        trace_dest=dest/'traces'/case['id']
        trace_dest.mkdir(parents=True)
        for file in (runtime/'traces').glob('*.jsonl'):
            shutil.copyfile(file,trace_dest/file.name)
            spans += [json.loads(l) for l in file.read_text(encoding='utf-8').splitlines()]
        names=[s['name'] for s in spans]
        checks['trajetoria']=('execute_tool registrar_triagem' in names)==expected['registro']
        checks['sem_erro_tecnico']=not final['motivo_termino'].startswith(('erro','limite','laco','validacao'))
        record={'id':case['id'],'entrada':case['entrada'],'origem':case['origem'],'classe':case['classe'],
                'esperado':expected,'inicial':initial,'saida':final,'repeticao':again,
                'banco':{'antes':before,'depois':after},'checks':checks,'aprovado':all(checks.values()),
                'segundos_end_to_end':round(time.monotonic()-start,4)}
        (dest/(case['id']+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        results.append(record)
        print(f'{index+1}/{len(dataset)} {case["id"]}: {record["aprovado"]}',flush=True)
    summary={'versao':VERSION,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'data':datetime.now(timezone.utc).isoformat(),'dataset_version':'1.0.0','dataset_hash':digest(dataset),
             'origens':{k:sum(r['origem']==k for r in results) for k in ('producao','desenvolvimento','sintetico')},
             'por_classe':{c:{'n':sum(r['classe']==c for r in results),'bons':sum(r['classe']==c and r['aprovado'] for r in results)} for c in sorted({r['classe'] for r in results})},
             'total':len(results),'aprovados':sum(r['aprovado'] for r in results),
             'juiz':'Critérios desta rodada são determinísticos/trajetória/resultado; juiz medido separadamente.'}
    (dest/'resumo.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': main()
