"""Gera somente números obtidos de arquivos reais e referências de código verificáveis."""
import inspect
import json
from pathlib import Path
from src.common import ROOT
from src.graph import App
from src.security import LocalAuthority, validate_episode, validate_fact
from src.version import VERSION
from src.graph import MAX_SECONDS


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
    metric_files=list((ROOT/'evals/resultados').glob('*/metricas.json'))
    metric_files.sort(key=lambda p:tuple(int(n) for n in next(iter(read(p))).split('.')))
    runs=[p.parent.name for p in metric_files]
    for run in runs:
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
    policy=read(ROOT/'evals/politica.json')
    judge_path=policy['validacao_juiz']
    judge=read(ROOT/judge_path)
    current_run=policy['rodada_atual']
    current_summary=read(ROOT/'evals/resultados'/current_run/'resumo.json')
    current_score=100*current_summary['aprovados']/current_summary['total']
    current_metrics=read(ROOT/'evals/resultados'/current_run/'metricas.json')[VERSION]
    agreement=judge.get('concordancia')
    raw_judge_summary=(f"LLM isolado: {100*judge['concordancia_llm_isolado']:.0f}%, preservado separadamente. "
                       if 'concordancia_llm_isolado' in judge else 'LLM isolado não medido separadamente nesta coleta. ')
    judge_summary=(f"Juiz híbrido (regra + LLM): concordância {100*agreement:.0f}% ({round(20*agreement)}/20), limiar {100*judge['limiar']:.0f}%, "
                   f"{'adotado' if judge['adotado'] else 'não adotado'}. "+
                   raw_judge_summary+
                   f"{len(judge['desacordos'])} desacordos, "
                   f"{'todos analisados' if judge.get('desacordos_analisados') else 'análise incompleta'}. "
                   f'Fonte: {judge_path}; matriz em docs/evals.md. '
                   'Revisor: Guilherme, conforme confirmação registrada; '
                   'metodologia e proveniência em evals/revisao/PROVENIENCIA-REVISAO.md.'
                   if agreement is not None else '**LACUNA:** revisão e matriz do juiz incompletas.')
    model_card=f'''# Model card — Agente de triagem de suporte de TI

## 1. Identificação

Sistema local acadêmico `triagem-ti`, versão {VERSION}. Continuação das Partes 1 e 2.
Autores do trabalho: Pedro Henrique Macedo Cunha e Guilherme dos Santos Medeiros.
Responsabilidade e ferramentas de apoio: docs/autoria.md.
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
| Até 3 chamadas de estágio, {MAX_SECONDS}s, 12000 tokens observados, 16 superpassos | src/graph.py constantes e call; tokens não são teto rígido de fatura |
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
O nome do SDK openai não altera quem presta a inferência. O juiz híbrido combina
o mesmo modelo com regra determinística da mensagem fixa de encaminhamento ao N1.
O LLM isolado e o resultado híbrido são medidos separadamente. A tentativa com
Mistral Small recebeu 429 e foi interrompida, sem adoção.

## 6. Dados

Corpus e dataset fictícios. Entrada livre pode conter dados reais indevidos e a
redação é parcial. Memória longa agora só aceita campos fechados de triagem e fatos
validados. **LACUNA:** base legal para uso real e retenção do provedor não definidas.
Mapeamento completo: docs/seguranca.md.

## 7. Avaliação

30 casos v1.0.0, nove de desenvolvimento e 21 sintéticos. Baseline 3.0.0: 3/30 (10%);
controles 3.1.0: 5/30 (16,7%). Rodada atual {VERSION}: {current_summary['aprovados']}/30
({current_score:.1f}%), em evals/resultados/{current_run}/resumo.json. Comparação em
evals/resultados/comparacao-atual.txt. Os erros 429 e as primeiras rodadas são
preservados como histórico, não apagados. Testes locais em logs/parte3/testes.md.
SLI operacional atual: {100*current_metrics['slo']['sli']:.2f}%, alvo 90%,
SLO {'violado' if current_metrics['slo']['violado'] else 'atingido na amostra'}.
{judge_summary}

## 8. Limites conhecidos

Busca lexical pode perder paráfrases; fonte existente não prova todas as afirmações;
regex hostil não cobre todos os ataques; memória tem perda deliberada de detalhe;
API com limite observado: intervalo local padrão de 35s, podendo aumentar a latência;
expiração e retenção exigem comandos, não daemon.
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

1. Juiz: repetir com amostra nova independente; a calibração atual reutiliza os vinte rótulos e não é teste cego.
2. Avaliação: ampliar a amostra e fazer revisão de domínio independente; autoria das revisões está nos metadados.
3. Provedor: comprovar capacidade sob carga; o espaçamento atende demonstração de baixo volume.
4. Credencial/plataforma: comprovar privilégios e gasto no console e auditar ACL.
5. Dados reais: definir finalidade/base legal, controles e contrato de retenção antes de uso.
6. Operação: instalar agendamento de expiração/limpeza e acesso individual autenticado.
7. Riscos: revisar a evolução da análise da Parte 2 em exercicios/aula14-respostas.md.
'''
    (ROOT/'docs/model-card.md').write_text(model_card,encoding='utf-8')


if __name__=='__main__':main()
