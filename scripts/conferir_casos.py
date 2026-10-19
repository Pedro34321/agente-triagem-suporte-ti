"""Critérios objetivos dos nove casos reais, separados da geração."""
import json
from src.common import ROOT
from src.contracts import Output


def main():
    directory = ROOT / 'logs/parte2'
    cases = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in directory.glob('caso_*.json')}
    checks = {}
    for name, case in cases.items():
        Output.model_validate(case['saida'])
        assert case['tipo'] == 'modelo_real'
    out = lambda name: cases[name]['saida']
    checks['simples'] = out('caso_simples')['categoria'] == 'Acesso / Conta' and out('caso_simples')['registro_id'] is not None
    checks['divergencia'] = out('caso_divergencia')['categoria'] == 'Rede / Conectividade' and any(s['id'].startswith('incidente:') for s in out('caso_divergencia')['fontes'])
    checks['inexistente'] = not out('caso_registro_inexistente')['suficiente'] and bool(out('caso_registro_inexistente')['perguntas']) and out('caso_registro_inexistente')['registro_id'] is None
    checks['informativo'] = out('caso_nao_dispara')['categoria'] == 'Solicitação Informativa' and not out('caso_nao_dispara')['registrar'] and out('caso_nao_dispara')['registro_id'] is None
    checks['fora_corpus'] = not out('caso_fora_corpus')['suficiente'] and out('caso_fora_corpus')['registro_id'] is None
    human = cases['caso_humano']
    checks['humano'] = human['inicial']['motivo_termino'] == 'aguardando_aprovacao' and human['aprovacao_roteirizada']['decisao'] == 'editar' and human['segunda_aprovacao']['ja_existia'] and human['registros_deste_caso'] == 1
    for name in ('caso_ambiguo', 'caso_incompleto'):
        checks[name] = not out(name)['suficiente'] and bool(out(name)['perguntas']) and out(name)['registro_id'] is None
    checks['fora_escopo'] = out('caso_fora_escopo')['motivo_termino'] == 'fora_escopo'
    report = {'criterios': checks, 'aprovados': sum(checks.values()), 'total': len(checks),
              'modelo': cases['caso_simples']['modelo'], 'commit_execucao': cases['caso_simples']['commit'],
              'chamadas_recuperacao': {name: sum(e.get('chamadas_recuperacao', 0) for e in c['eventos']) for name, c in cases.items()},
              'tokens': {name: sum(e.get('tokens', 0) for e in c['eventos']) for name, c in cases.items()},
              'segundos': {name: c['segundos'] for name, c in cases.items()},
              'bytes_memoria': {name: [e['memoria']['bytes'] for e in c['eventos'] if e.get('node') == 'registrar'] for name, c in cases.items()}}
    (directory / 'conferencia-casos.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == '__main__':
    main()
