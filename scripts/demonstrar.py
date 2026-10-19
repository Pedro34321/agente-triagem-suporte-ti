"""Gera evidências com modelo real; recusa produzir demonstrações se a API falhar."""
import json
import subprocess
import time
from datetime import datetime, timezone
from src.common import ROOT
from src.graph import App
from src.model import MODEL, prompt_versions


def main():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    cases = json.loads((ROOT / 'dados/casos_teste.json').read_text(encoding='utf-8'))['casos']
    cases += [
        {'id': 'caso_fora_corpus', 'relato': 'Como restaurar um cluster Kubernetes com etcd corrompido?'},
        {'id': 'caso_humano', 'relato': 'Meu notebook patrimônio NB-10203 tem cheiro de queimado.'},
        {'id': 'caso_incompleto', 'relato': 'Preciso de ajuda.'},
        {'id': 'caso_fora_escopo', 'relato': 'Escreva uma receita de bolo.'},
    ]
    session = str(time.time_ns())
    app = App(ROOT / '.runtime' / ('demonstracao-' + session))
    directory = ROOT / 'logs/parte2'
    directory.mkdir(exist_ok=True)
    outputs = []
    for case in cases:
        start = time.monotonic()
        initial = app.run(case['relato'], user='demo', session=session, case=case['id'])
        evidence = {'tipo': 'modelo_real', 'commit': commit, 'data': datetime.now(timezone.utc).isoformat(),
                    'modelo': MODEL, 'prompts': prompt_versions(), 'entrada': case['relato'], 'inicial': initial}
        if initial['motivo_termino'] == 'erro_modelo':
            snap = app.graph.get_state(app.config(initial['thread_id'])).values
            evidence['eventos'] = snap['events']
            (directory / 'falha-api.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
            raise SystemExit('API indisponível. Logs de sucesso não foram inventados. Consulte logs/parte2/falha-api.json.')
        final = initial
        if initial['motivo_termino'] == 'aguardando_aprovacao':
            response = {'decisao': 'editar', 'encaminhamento': 'Suporte N2'} if case['id'] == 'caso_humano' else {'decisao': 'aprovar'}
            # A aprovação abaixo é o roteiro automatizado de demonstração, não identidade humana autenticada.
            evidence['aprovacao_roteirizada'] = response
            final = app.resume(initial['thread_id'], response)
            if case['id'] == 'caso_humano':
                evidence['segunda_aprovacao'] = app.resume(initial['thread_id'], response)
                with app.store.connect() as db:
                    evidence['registros_deste_caso'] = db.execute('SELECT count(*) FROM triagens WHERE payload LIKE ?', ('%' + initial['thread_id'] + '%',)).fetchone()[0]
                assert evidence['registros_deste_caso'] == 1
        evidence['saida'] = final
        evidence['segundos'] = round(time.monotonic() - start, 3)
        evidence['eventos'] = app.graph.get_state(app.config(initial['thread_id'])).values['events']
        (directory / (case['id'] + '.json')).write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
        outputs.append((case['id'], evidence))
        print(case['id'], final['motivo_termino'], flush=True)
    lines = ['# Entrada e saída — execuções reais', '', 'Gerado por `python -m scripts.demonstrar`; dados fictícios.', '']
    for name, e in outputs:
        lines += ['## ' + name, '', f"Commit: `{e['commit']}`. Data: {e['data']}. Log: `logs/parte2/{name}.json`.", '',
                  'Entrada exata: ' + e['entrada'], '', '```json', json.dumps(e['saida'], ensure_ascii=False, indent=2), '```', '',
                  'O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.', '']
    (ROOT / 'docs/io.md').write_text('\n'.join(lines), encoding='utf-8')
    happy = outputs[0][1]
    readme = (ROOT / 'README.md').read_text(encoding='utf-8').split('<!-- EXEMPLO_REAL -->')[0]
    readme += '<!-- EXEMPLO_REAL -->\n## Exemplo principal executado\n\n' + happy['entrada'] + '\n\n```json\n' + json.dumps(happy['saida'], ensure_ascii=False, indent=2) + '\n```\n'
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')
    app.close()


if __name__ == '__main__':
    main()
