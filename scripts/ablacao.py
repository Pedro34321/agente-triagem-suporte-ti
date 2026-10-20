"""A/B real; não executa automaticamente junto dos testes offline."""
import json
import subprocess
from datetime import datetime, timezone
from src.common import ROOT
from src.model import LLM, prompt, MODEL
from src.knowledge import search
from src.contracts import DraftDecision


def main():
    phrase = 'Não associe senha individual a rede coletiva.'
    original = prompt('responder')
    assert phrase in original
    cases = ['Minha senha do email está incorreta.', 'Conta bloqueada só para mim.',
             'Senha incorreta no Andar 3.', 'Esqueci a senha da conta corporativa.',
             'Meu email rejeita a credencial mas os colegas conseguem entrar.']
    llm, results = LLM(), []
    for text in cases:
        for treatment, system in [('com_frase', original), ('sem_frase', original.replace(phrase, ''))]:
            data = {'relato': text, 'fontes': search('senha conta', 'acesso'), 'erros_ferramentas': [], 'memorias': []}
            output, tokens = llm.call('responder', DraftDecision, data, override=system)
            results.append({'tratamento': treatment, 'entrada': text, 'saida': output, 'tokens': tokens,
                            'acerto_categoria': output['categoria'] == 'Acesso / Conta'})
    report = {'data': datetime.now(timezone.utc).isoformat(), 'modelo': MODEL, 'frase_removida': phrase,
              'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'resultados': results}
    (ROOT / 'logs/parte2/ablacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Experimento salvo. Revisar resultados antes de remover a frase definitivamente.')


if __name__ == '__main__':
    main()
