# Guia da entrega — Parte 3

Autores: **Pedro Henrique Macedo Cunha e Guilherme dos Santos Medeiros**.
Sistema local acadêmico, versão 3.2.1. Autoria e responsabilidade: docs/autoria.md.

## Resultado atual

- Casos completos: **29/30 (96.7%)**, mesmos casos e critérios das primeiras versões.
- Juiz híbrido 1.2.0: **90.0%** de concordância, limiar de 90%; **adotado na amostra de calibração**.
- LLM isolado: **85.0%**, abaixo do limiar, preservado separadamente.
- SLI operacional: **98.08%**, alvo de 90%; SLO atingido na amostra.
- Testes locais: **31 passaram**, sem novas chamadas de API.

Os 90% pertencem ao juiz híbrido, com regra de consistência para a mensagem fixa de
encaminhamento ao N1; o LLM isolado não atingiu 90%. Os indicadores são diferentes.
Os números medem as amostras de desenvolvimento
e calibração; não constituem garantia de eficácia em produção ou em casos inéditos.
As primeiras rodadas com 429 e juiz de 45% continuam no repositório como histórico.

## Onde conferir as exigências

| Frente | Evidência |
|---|---|
| Sistema da Parte 2 | StateGraph, RAG, memória, checkpoint e aprovação mantidos em src/ |
| Dataset e suíte | 30 casos, sete classes, recusas e origem/revisão; evals/dataset.json e evals/rodar.py |
| Resultado e trajetória | banco antes/depois, duplicata idempotente e spans por caso, nas pastas de rodada |
| Juiz | vinte votos/notas/revisor, rubrica, matriz atual e histórico; docs/evals.md e evals/revisao/ |
| Governança | model card com doze campos, autoridade e reconstrução de decisão pelos traces |
| Segurança | riscos OWASP, controles fora do prompt e testes; dados e riscos aceitos em docs/seguranca.md |
| Observabilidade | traces OTel, métricas por versão, quatro perguntas e SLO em docs/observabilidade.md |
| Projeto | README, requirements fixado, env vazio, documentação Markdown e testes |
| Opcionais | ausência de multiagente, MCP e multimídia declarada em docs/opcionais.md |

Fontes dos números atuais: `evals/resultados/ritmo-3-2-1-20261122/resumo.json`, `metricas.json` e
`evals/revisao/juiz-hibrido-1-2-0/validacao-juiz.json`. A revisão foi conferida por Guilherme conforme confirmação
registrada pelo usuário; metodologia e origem em evals/revisao/PROVENIENCIA-REVISAO.md.

## Conferir sem novas chamadas pagas

```powershell
python -m pytest -q
python -m evals.calibrar_juiz --consolidar
python -m evals.comparar evals/resultados/baseline-3-0-0 evals/resultados/ritmo-3-2-1-20261122
python -m evals.metricas evals/resultados/ritmo-3-2-1-20261122
python -m scripts.relatorio_parte3
```

## Limites que devem ser explicados

O espaçamento de 35s entre chamadas é deliberado: o plano Mistral limitou as primeiras
rodadas. A versão atual perde vazão e pode demorar. A rubrica do juiz foi corrigida
após observar a mesma amostra; nova validação independente continua necessária.
As LACUNAS de produção permanecem: ACL Windows, credencial empresarial, contrato e
retenção do provedor, base para dados reais, revisão de domínio e operação sob carga.
Não afirmar que não há falhas, que o agente é seguro contra todo ataque ou que uma
meta atingida nesta amostra prova prontidão empresarial.

## Entregar

Enviar o repositório com esta versão integrada à main. Se o PR de correção ainda não
estiver integrado, usar a branch codex/parte3-meta90. Não enviar .env.local, .runtime,
credenciais ou o ambiente virtual. Os exemplos e traces versionados são fictícios.
