"""Importa o Markdown preenchido por uma pessoa, sem inventar respostas ausentes."""
import argparse
import json
import re
from pathlib import Path
from src.common import ROOT


def main():
    p=argparse.ArgumentParser();p.add_argument('arquivo');a=p.parse_args()
    text=Path(a.arquivo).read_text(encoding='utf-8')
    labels={}
    for chunk in re.split(r'(?m)^## ',text)[1:]:
        id=chunk.splitlines()[0].strip()
        vote=re.search(r'(?im)^Rótulo humano \(SIM/NÃO\):\s*(SIM|NÃO|NAO)\s*$',chunk)
        reason=re.search(r'(?m)^Razão:\s*(.+)$',chunk)
        reviewer=re.search(r'(?m)^Revisor humano:\s*(.+)$',chunk)
        if not vote or not reason or not reviewer or '_' in reason[1] or '_' in reviewer[1]:
            raise SystemExit('Revisão incompleta em '+id)
        labels[id]={'humano':vote[1].upper()=='SIM','nota_humana':reason[1].strip(),'revisor_humano':reviewer[1].strip()}
    path=ROOT/'evals/revisao/rotulos-humanos.json'
    packet=json.loads(path.read_text(encoding='utf-8'))
    if len(labels)!=20 or set(labels)!={c['id'] for c in packet}: raise SystemExit('São necessários os vinte ids originais.')
    for c in packet:c.update(labels[c['id']])
    path.write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Vinte rótulos humanos importados; nenhum campo foi inferido.')


if __name__=='__main__':main()
