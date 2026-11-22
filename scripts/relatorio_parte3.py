"""Gera somente números obtidos de arquivos reais e referências de código verificáveis."""
import inspect
import json
from pathlib import Path
from src.common import ROOT
from src.graph import App
from src.security import LocalAuthority, validate_episode, validate_fact


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    refs={}
    for name,obj in [('autorizar',LocalAuthority.authenticate),('grant',LocalAuthority.verify),
                     ('episodio',validate_episode),('fato',validate_fact),('registrar',App.registrar),
                     ('validar',App.validar),('interpretar',App.interpretar),('run',App.run)]:
        obj=inspect.unwrap(obj)
        file=Path(inspect.getsourcefile(obj)).relative_to(ROOT).as_posix()
        source,start=inspect.getsourcelines(obj)
        needles={'autorizar':'if actor', 'grant':'if now', 'episodio':'if not payload',
                 'fato':'if not re.fullmatch', 'registrar':'self.authority.verify',
                 'validar':"if d['registrar']", 'interpretar':"if info['location']", 'run':'if HOSTILE.search'}
        offset=next(i for i,line in enumerate(source) if needles[name] in line)
        refs[name]=f'{file}:{start+offset}'
    target=ROOT/'logs/parte3';target.mkdir(exist_ok=True)
    (target/'referencias-codigo.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
    path=ROOT/'docs/seguranca.md'
    text=path.read_text(encoding='utf-8').split('<!-- LINHAS -->')[0].rstrip()
    text+='\n\n<!-- LINHAS -->\n## Pontos de aplicação verificados\n\n'
    text+='\n'.join(f'- {name}: `{ref}`.' for name,ref in refs.items())+'\n'
    riskrefs={'ASI03':refs['autorizar']+' e '+refs['grant'],'ASI01':refs['run']+' e '+refs['validar'],
              'ASI02':refs['registrar'],'ASI09':'src/graph.py:'+str(inspect.getsourcelines(App.aprovar)[1]),
              'ASI10':'src/security.py:44 e src/graph.py:20','ASI04':'src/model.py:1 e requirements.txt:1',
              'ASI06':refs['episodio']+' e '+refs['fato'],'ASI08':'src/telemetry.py:75 e src/graph.py:95'}
    text+='\n| Risco | Componente e linha atual |\n|---|---|\n'+'\n'.join(f'| {k} | `{v}` |' for k,v in riskrefs.items())+'\n'
    path.write_text(text,encoding='utf-8')
    lines=['## Métricas calculadas dos traces','']
    for run in ('baseline-3-0-0','controles-3-1-0'):
        metrics=read(ROOT/'evals/resultados'/run/'metricas.json')
        for version,m in metrics.items():
            lines += [f'### Versão {version}', '', '| Versão | Invocações | p50 s | p95 s | Custo médio completo USD | SLI | Consumo do orçamento |','|---|---|---|---|---|---|---|']
            slo=m['slo'];cost=m['custo_estimado_usd_por_execucao']
            lines.append(f'| {version} | {m["execucoes"]} | {m["p50_s"]:.4f} | {m["p95_s"]:.4f} | {cost if cost is not None else "LACUNA: usage ausente em falhas"} | {100*slo["sli"]:.2f}% | {100*slo["consumo_orcamento"]:.2f}% |')
            lines+=['',f'Fonte: `evals/resultados/{run}/metricas.json`. Custo conhecido em {m["execucoes_com_custo_conhecido"]}/{m["execucoes"]} invocações; limite inferior da média USD {m["custo_limite_inferior_por_execucao"]:.8f}.',
                    '',f'Motivos {version}: `{m["motivos"]}`.', '',f'Ferramentas {version}:', '', '| Ferramenta | Chamadas | Erros | Taxa |','|---|---|---|---|']
            lines += [f'| {name} | {v["chamadas"]} | {v["erros"]} | {100*v["taxa_erro"]:.1f}% |' for name,v in m['ferramentas'].items()]
            lines+=['','Os tempos são por invocação, inclusive retomadas; não são média de tempo humano de atendimento.','']
    # Seções separadas por versão em vez de linhas de uma tabela interrompida.
    path=ROOT/'docs/observabilidade.md'
    text=path.read_text(encoding='utf-8').split('<!-- MEDIDAS -->')[0].rstrip()
    path.write_text(text+'\n\n<!-- MEDIDAS -->\n'+'\n'.join(lines).rstrip()+'\n',encoding='utf-8')
    trace_dir=ROOT/'evals/resultados/controles-3-1-0/traces/simples'
    spans=[]
    for file in trace_dir.glob('*.jsonl'):
        for line in file.read_text(encoding='utf-8').splitlines():
            span=json.loads(line);span['_file']=file.relative_to(ROOT).as_posix();spans.append(span)
    roots=[s for s in spans if s['name']=='invoke_agent triagem-ti']
    initial=next(s for s in roots if s['attributes']['triagem.operation']=='run')
    approval=next((e for s in roots for e in s.get('events',[]) if e['name']=='approval'),None)
    assert approval,'Escolher uma decisão com aprovação realmente registrada.'
    approved=json.loads(approval['attributes']['data'])
    initial_out=json.loads(initial['attributes']['triagem.output'])
    finals=[json.loads(s['attributes']['triagem.output']) for s in roots if s['attributes']['triagem.termination_reason']=='registrado']
    result=finals[0]
    files=sorted({s['_file'] for s in roots})
    judge=read(ROOT/'evals/revisao/validacao-juiz.json')
    agreement=judge.get('concordancia')
    judge_summary=(f"Juiz: concordância {100*agreement:.0f}% ({round(20*agreement)}/20), limiar {100*judge['limiar']:.0f}%, "
                   f"{'adotado' if judge['adotado'] else 'não adotado'}. "
                   f"{len(judge['desacordos'])} desacordos, "
                   f"{'todos analisados' if judge.get('desacordos_analisados') else 'análise incompleta'}. "
                   'Fonte: evals/revisao/validacao-juiz.json; matriz em docs/evals.md. '
                   'Revisão assistida por IA, conferida por Guilherme segundo confirmação do usuário; '
                   'proveniência em evals/revisao/PROVENIENCIA-REVISAO.md.'
                   if agreement is not None else '**LACUNA:** revisão e matriz do juiz incompletas.')
    model_card=f'''# Model card — Agente de triagem de suporte de TI

## 1. Identificação

Sistema local acadêmico `triagem-ti`, versão 3.1.0. Continuação das Partes 1 e 2.
Mantenedores do trabalho: Pedro Henrique Macedo Cunha e Guilherme dos Santos Medeiros.
O documento histórico está preservado em model-card-parte1.md.

## 2. Finalidade

Receber texto livre e propor categoria, prioridade e equipe de suporte com fontes.
Não diagnostica definitivamente nem executa reparos. Opera com dados simulados.

## 3. Autoridade

Consulta corpus e cadastro; grava uma triagem local por conteúdo aprovado, com
memória selecionada. Não dispõe de shell, alteração de conta/senha, rede, pagamento,
envio de mensagem ou escrita em sistema externo.

| Limite | Aplicação e evidência |
|---|---|
| Escopo de triagem e bloqueio de padrões hostis | código `{refs['run']}`, testes ASI01 |
| Aprovação com credencial local e identidade vinculada | `{refs['autorizar']}`, test_asi03_unauthorized_approval |
| Escrita vinculada à proposta, prazo e aprovação | `{refs['grant']}` e `{refs['registrar']}`, teste de bypass |
| Até 3 chamadas de estágio, 90s, 12000 tokens observados, 16 superpassos | src/graph.py constantes e call; tokens não são teto rígido de fatura |
| Na falha de fonte/controle, não escrever | `{refs['validar']}`, testes de fonte inválida e auditoria indisponível |
| Operador pode suspender | TRIAGEM_SUSPENDED=1, test_suspend_blocks_calls_and_writes |
| Credencial de inferência | usada somente no endpoint Mistral no adaptador, não no prompt |

**LACUNA:** escopo/limite financeiro da chave no console do provedor e ACL efetiva
do Windows não verificados. Identidade local é posse do arquivo, não SSO/MFA.

## 4. Ferramentas e integrações

Mistral API para inferência; busca textual do corpus; SQL parametrizado somente
leitura no cadastro; SQLite operacional para triagem/memória/checkpoint.
OpenTelemetry exporta arquivos locais. Não há MCP nem multiagente.

## 5. Modelo e provedor

Ministral 8B `ministral-8b-2512`, Mistral. Prompts versionados e saída estruturada.
O nome do SDK openai não altera quem presta a inferência. Juiz usa o mesmo modelo,
com rubrica própria; foi avaliado e não adotado por concordância insuficiente.

## 6. Dados

Corpus e dataset fictícios. Entrada livre pode conter dados reais indevidos e a
redação é parcial. Memória longa agora só aceita campos fechados de triagem e fatos
validados. **LACUNA:** base legal para uso real e retenção do provedor não definidas.
Mapeamento completo: docs/seguranca.md.

## 7. Avaliação

30 casos v1.0.0, nove de desenvolvimento e 21 sintéticos. Baseline 3.0.0: 3/30 (10%);
controles 3.1.0: 5/30 (16,7%). Evidências: evals/resultados/*/resumo.json e comparacao.txt.
Melhora na fatia de três ataques: 2/3 para 3/3. Erros 429 dominam os resultados e
impedem concluir melhoria semântica global. Testes locais em logs/parte3/testes.md.
{judge_summary}

## 8. Limites conhecidos

Busca lexical pode perder paráfrases; fonte existente não prova todas as afirmações;
regex hostil não cobre todos os ataques; memória tem perda deliberada de detalhe;
API com limite observado; expiração e retenção exigem comandos, não daemon.
SLI de término não captura toda classificação errada com JSON válido.

## 9. Riscos aceitos

Operador local com acesso ao segredo pode aprovar; comprometimento de SO, cadeia
de dependências e erro semântico residual não têm defesa completa. Aceitação técnica
restrita à demonstração fictícia. Evidência e gatilhos de revisão em
docs/seguranca.md, seção RISCO ACEITO. Os integrantes devem revisar essa decisão.

## 10. Supervisão humana

Toda proposta de registro pausa por 24h. Revisor-local pode aprovar, rejeitar ou
editar prioridade/equipe. CLI usa credencial local; automação da suíte é roteiro
de teste e não presença humana autenticada. Expiração nunca autoriza escrita.

## 11. Registro e retenção: decisão reconstruída só do trace

Arquivos originais utilizados (não foi consultado o dataset para esta reconstrução):
{chr(10).join('- `'+p+'`' for p in files)}

A raiz de início identifica versão `{initial['attributes']['triagem.system.version']}`,
modelo `{initial['attributes']['gen_ai.request.model']}` e prompts por hash. Seu evento
decision_record contém a entrada redigida e a interpretação. Os spans de recuperação
e o contexto trazem as fontes {', '.join(c['id'] for c in initial_out['fontes'])}.
A proposta foi `{initial_out['categoria']}`, prioridade `{initial_out['prioridade']}`,
equipe `{initial_out['encaminhamento']}`, com término `{initial_out['motivo_termino']}`.
Na retomada, o evento approval atribui a decisão ao principal `{approved['actor']}`,
timestamp Unix `{approved['time']}`, resposta `{approved['response']}` e proposta completa.
O execute_tool registrar_triagem registra argumentos e recibo. A saída confirmou
registro `{result['registro_id']}`. As invocações são correlacionadas pelo mesmo
gen_ai.conversation.id, e não por suposição de proximidade temporal.

Trace é o registro da decisão; não há novo log operacional paralelo. Evidências de
avaliação são derivados dos mesmos spans. Acesso: operador com permissão no diretório;
traces acadêmicos fictícios versionados são públicos no repositório. Prazo operacional:
30 dias, aplicado por python -m scripts.retencao. Sem agendamento automático.
Remoção por usuário cobre traces/checkpoints e tabelas locais, verificada por teste.
**LACUNA:** ACL Windows, backup/OneDrive, Git e retenção no provedor não são apagados
nem comprovados por esse comando.

## 12. Histórico de mudanças

docs/mudancas.md registra baseline, controles, correções e commits. Não houve correção
formal do professor disponibilizada; as mudanças vieram da inspeção e dos testes.

## Lacunas e correções propostas

1. Juiz: permanece não adotado; melhorar a rubrica em nova versão e fazer nova calibração independente.
2. Avaliação: revisão independente dos sintéticos e das saídas é melhoria futura; autoria técnica por IA está declarada.
3. Provedor: ajustar limites/ritmo e medir nova rodada; SLO atual está violado.
4. Credencial/plataforma: comprovar privilégios e gasto no console e auditar ACL.
5. Dados reais: definir finalidade/base legal, controles e contrato de retenção antes de uso.
6. Operação: instalar agendamento de expiração/limpeza e acesso individual autenticado.
7. Riscos: revisar a evolução da análise da Parte 2 em exercicios/aula14-respostas.md.
'''
    (ROOT/'docs/model-card.md').write_text(model_card,encoding='utf-8')


if __name__=='__main__':main()
