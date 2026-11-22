# Observabilidade — Parte 3

## Plano declarado antes de medir

| Interessado | Pergunta | Decisão que muda |
|---|---|---|
| Negócio | a triagem chega a um término útil/seguro? | promover a versão ou manter apenas demonstração local |
| Operação | quais falhas do modelo/ferramenta e latências aparecem? | investigar provedor, banco ou fluxo |
| Quem paga | quanto token/custo cada execução consome? | limitar uso e revisar contexto/modelo |
| Responsável | conseguimos reconstruir a fonte, versão e autorização da escrita? | aceitar auditoria, bloquear gravação ou suspender |

SLO pré-declarado em `evals/politica.json`: ao menos 90% de execuções com término
considerado bom em janela móvel de sete dias. Não foi ajustado para acomodar o resultado.

## Instrumentação e árvore

SDK OpenTelemetry real, exportador JSONL síncrono em `.runtime/traces/<trace_id>.jsonl`.
Não se simula um trace apenas renomeando um log. Spans reais têm ids, parent_id,
início/fim, atributos, eventos e status. Convenções GenAI em desenvolvimento:

```text
invoke_agent triagem-ti (uma invocação da CLI iniciar ou retomar)
  chat ministral-8b-2512 (interpretação)
  execute_tool buscar_corpus
  execute_tool consultar_cadastro
  execute_tool lembrar_episodios
  execute_tool ler_fato
  chat ministral-8b-2512 (proposta, eventualmente correção)
  audit_preflight
  execute_tool registrar_triagem (após aprovação)
  execute_tool gravar_episodio
  execute_tool gravar_fato (quando houver)
```

A pausa termina uma invocação com `aguardando_aprovacao`; a retomada abre outro trace.
As duas são correlacionadas por gen_ai.conversation.id. Não há span artificial aberto
por 24 horas nem soma do tempo humano à latência de inferência.

A raiz guarda versão do sistema, modelo/provedor, operação, proprietário pseudônimo,
entrada redigida, hashes de prompts, saída e motivo de término. Eventos carregam
interpretação, ids/contexto recuperado, ferramentas e revisão (principal local,
timestamp, proposta e decisão). O principal identifica a credencial local, não prova
presença física de um analista. Tokens de entrada/saída vêm do usage do provedor.

Como consultar:

```powershell
python -m scripts.ver_traces CAMINHO_DO_ARQUIVO.jsonl
python -m evals.metricas evals/resultados/controles-3-1-0
```

Arquivo é o destino consultável permitido no enunciado. Não há painel/collector remoto.
As evidências das rodadas são copiadas para suas próprias pastas traces/, com dados fictícios.

## Modos de falha

| Falha | Silenciosa? | Sinal |
|---|---|---|
| Categoria incorreta com JSON válido | sim | check determinístico do caso, ligado à rodada/trace; SLI de término sozinho não detecta toda semântica |
| Resposta vaga ou recusa indevida sem exceção técnica | sim | revisão de casos; juiz avaliado com 45% de concordância e não adotado: LACUNA de detecção automática confiável |
| Orçamento esgotado sem erro de ferramenta | sim | termination_reason limite_* / quality.good=false |
| API devolve 429 | não | chat com error.type e raiz erro_modelo |
| Cadastro retorna inexistente | erro de domínio recuperável | execute_tool consultar_cadastro com error.type registro_nao_encontrado |
| Repetição de aprovação gera duplicação | pode ser | teste de resultado consulta contagem e identificador |
| Exportador falha | não no registro | preflight impede escrita; risco de falha posterior permanece |

## SLI, objetivo e orçamento de erro

Evento válido = raiz invoke_agent de uma invocação real do sistema, com versão e
motivo de término, excluindo spans de juiz e execuções de testes com double.
Bom = `triagem.quality.good=true`, derivado de termination_reason em:
registrado, informativo, base_insuficiente, incompleto, ambiguo, fora_escopo,
aguardando_aprovacao, rejeitado ou politica_bloqueou. Erro, orçamento, validação
falha e expiração não contam como bons. Recusar corretamente é um resultado útil.

SLI = bons / válidos. Alvo >=90%, janela 7 dias, orçamento = 10% dos válidos.
Consumo = maus / orçamento. A janela medida é o lote de execuções desta data,
contido nos sete dias, não sete dias de serviço empresarial. O indicador mede término
operacional útil/seguro e não acurácia semântica; avaliação por classe o complementa.

## Resultados medidos e decisões

As tabelas numéricas e referências aos arquivos são acrescentadas pelo relatório
`scripts/relatorio_parte3.py`, sem misturar versões. A baseline tem 32 invocações
e a versão com controles 34, porque início e retomadas/repetições são invocações
distintas. Cada rodada tem 30 casos do dataset.

O SLO foi **violado** nas duas rodadas por indisponibilidade/limite da Mistral.
Não promover para operação; investigar limites do plano e espaçamento das chamadas
e só então repetir as medições em uma nova rodada, preservando as atuais.

Latências baixas podem significar rejeição rápida da API, não um agente melhor.
Custos são estimativas pelos tokens informados e tabela de US$0,15/milhão tanto
entrada como saída, sem desconto de cache. Chamadas com erro e sem usage têm custo
desconhecido: não são contabilizadas como custo zero nem usadas para inventar uma fatura.
O relatório informa cobertura de usage e limite inferior da média quando há lacunas.

As respostas às quatro perguntas são: (1) não há base operacional para promover;
(2) o provedor concentra as falhas, ferramentas tiveram pouca exposição e zero erros
não prova robustez; (3) custo integral não é inferível sem usage de falhas;
(4) traces de escrita bem-sucedida permitem reconstruir a decisão e a autorização
local, mas identidade humana forte e ACL de produção permanecem lacunas.

Fontes técnicas consultadas em 13/11/2026:
https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md
https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/execute-tool.md
https://docs.mistral.ai/inference/pricing

<!-- MEDIDAS -->
## Métricas calculadas dos traces

### Versão 3.0.0

| Versão | Invocações | p50 s | p95 s | Custo médio completo USD | SLI | Consumo do orçamento |
|---|---|---|---|---|---|---|
| 3.0.0 | 32 | 0.7633 | 4.5952 | LACUNA: usage ausente em falhas | 15.62% | 843.75% |

Fonte: `evals/resultados/baseline-3-0-0/metricas.json`. Custo conhecido em 5/32 invocações; limite inferior da média USD 0.00001283.

Motivos 3.0.0: `{'erro_modelo': 27, 'fora_escopo': 2, 'aguardando_aprovacao': 1, 'registrado': 2}`.

Ferramentas 3.0.0:

| Ferramenta | Chamadas | Erros | Taxa |
|---|---|---|---|
| buscar_corpus | 2 | 0 | 0.0% |
| consultar_cadastro | 2 | 0 | 0.0% |
| lembrar_episodios | 2 | 0 | 0.0% |
| ler_fato | 2 | 0 | 0.0% |
| registrar_triagem | 1 | 0 | 0.0% |

Os tempos são por invocação, inclusive retomadas; não são média de tempo humano de atendimento.

### Versão 3.1.0

| Versão | Invocações | p50 s | p95 s | Custo médio completo USD | SLI | Consumo do orçamento |
|---|---|---|---|---|---|---|
| 3.1.0 | 34 | 0.6383 | 3.4490 | LACUNA: usage ausente em falhas | 26.47% | 735.29% |

Fonte: `evals/resultados/controles-3-1-0/metricas.json`. Custo conhecido em 9/34 invocações; limite inferior da média USD 0.00001515.

Motivos 3.1.0: `{'erro_modelo': 25, 'politica_bloqueou': 3, 'registrado': 4, 'aguardando_aprovacao': 2}`.

Ferramentas 3.1.0:

| Ferramenta | Chamadas | Erros | Taxa |
|---|---|---|---|
| buscar_corpus | 2 | 0 | 0.0% |
| consultar_cadastro | 2 | 0 | 0.0% |
| lembrar_episodios | 2 | 0 | 0.0% |
| ler_fato | 2 | 0 | 0.0% |
| registrar_triagem | 2 | 0 | 0.0% |
| gravar_episodio | 2 | 0 | 0.0% |
| gravar_fato | 1 | 0 | 0.0% |

Os tempos são por invocação, inclusive retomadas; não são média de tempo humano de atendimento.
