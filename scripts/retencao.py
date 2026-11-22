"""Limpeza operacional explícita; não promete apagar backups, Git ou o provedor."""
import argparse
import json
import time
from src.graph import get_app


def purge(app,days=30,now=None):
    cutoff=(now or time.time())-days*86400
    threads=set(); files=[]
    for file in (app.directory/'traces').glob('*.jsonl'):
        if file.stat().st_mtime < cutoff:
            for line in file.read_text(encoding='utf-8').splitlines():
                span=json.loads(line)
                thread=span.get('attributes',{}).get('gen_ai.conversation.id')
                if thread:threads.add(thread)
            files.append(file)
    for thread in threads:app.checkpointer.delete_thread(thread)
    for file in files:file.unlink()
    return {'traces_removidos':len(files),'threads_expiradas':len(threads),'prazo_dias':days}


def main():
    p=argparse.ArgumentParser();p.add_argument('--dias',type=int,default=30);a=p.parse_args()
    if a.dias<1:p.error('Prazo mínimo: um dia.')
    print(json.dumps(purge(get_app(),a.dias)))


if __name__=='__main__':main()
