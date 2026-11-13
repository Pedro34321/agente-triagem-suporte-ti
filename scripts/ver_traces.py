import argparse
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('arquivo');a=p.parse_args()
    spans=[json.loads(l) for l in Path(a.arquivo).read_text(encoding='utf-8').splitlines()]
    def visit(parent=None,depth=0):
        for s in spans:
            if s['parent_id']==parent:
                print('  '*depth+s['name']+' '+json.dumps(s['attributes'],ensure_ascii=False))
                for e in s.get('events',[]): print('  '*(depth+1)+'EVENTO '+e['name']+' '+str(e['attributes']))
                visit(s['context']['span_id'],depth+1)
    visit()


if __name__=='__main__': main()
