"""Verifica valores conhecidos no histórico sem imprimir matches ou conteúdo."""
import json
import re
import subprocess
from src.common import ROOT


def main():
    commits=subprocess.check_output(['git','rev-list','--all'],cwd=ROOT,text=True).splitlines()
    seen=set();hits=[]
    pattern=re.compile(rb'(?:sk-(?:proj-)?|mstrl_)[A-Za-z0-9_-]{25,}')
    for commit in commits:
        entries=subprocess.check_output(['git','ls-tree','-r',commit],cwd=ROOT,text=True).splitlines()
        for entry in entries:
            meta,path=entry.split('\t',1);sha=meta.split()[2]
            if sha in seen:continue
            seen.add(sha)
            if path.endswith(('.db','.sqlite','.png','.jpg','.mp4','.pdf')):continue
            data=subprocess.check_output(['git','cat-file','blob',sha],cwd=ROOT)
            if pattern.search(data):hits.append({'commit':commit,'arquivo':path,'tipo':'padrao_de_credencial','valor':'OMITIDO'})
    checks={
        'git log --all --oneline -- .env':subprocess.check_output(['git','log','--all','--oneline','--','.env'],cwd=ROOT,text=True),
        'git log --all -S OPENAI_API_KEY= --oneline':subprocess.check_output(['git','log','--all','-S','OPENAI_API_KEY=','--oneline'],cwd=ROOT,text=True)}
    report={'commits_verificados':len(commits),'blobs_unicos':len(seen),'deteccoes':hits,'comandos':checks,
            'limitacao':'Varredura por prefixos conhecidos não é prova de ausência de todo segredo ou formato possível.'}
    dest=ROOT/'logs/parte3';dest.mkdir(exist_ok=True)
    (dest/'auditoria-segredos.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Auditoria:',len(commits),'commits;',len(hits),'detecções; valores nunca impressos.')
    raise SystemExit(bool(hits))


if __name__=='__main__':main()
