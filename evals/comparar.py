import argparse
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('A');p.add_argument('B');a=p.parse_args()
    x,y=[json.loads((Path(t)/'resumo.json').read_text(encoding='utf-8')) for t in (a.A,a.B)]
    if x['dataset_hash']!=y['dataset_hash']: raise SystemExit('Datasets diferentes: comparação bloqueada.')
    print(f'DATASET v{x["dataset_version"]}  {x["total"]} casos  {x["origens"]}')
    print('JUIZ rubrica v1.0.0  concordância PENDENTE  limiar 90%  não adotado')
    print(f'classe                 {x["versao"]:>10} {y["versao"]:>10} delta pp')
    for c in x['por_classe']:
        aa=x['por_classe'][c];bb=y['por_classe'][c]
        av=100*aa['bons']/aa['n'];bv=100*bb['bons']/bb['n']
        print(f'{c:22} {av:9.1f}% {bv:9.1f}% {bv-av:+.1f}')
    av=100*x['aprovados']/x['total'];bv=100*y['aprovados']/y['total']
    print(f'MÉDIA (micro)          {av:9.1f}% {bv:9.1f}% {bv-av:+.1f}')


if __name__=='__main__': main()
