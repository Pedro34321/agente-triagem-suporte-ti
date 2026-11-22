# Mudanças desde a Parte 2

Não foi fornecida correção formal do professor. Os defeitos abaixo foram identificados
por inspeção e testes. O sistema-base LangGraph, contratos, RAG e checkpoint foi mantido.

| Commit | Mudança e motivo |
|---|---|
| 2fdc11d | baseline 3.0.0, traces OpenTelemetry e suíte de 30 casos pela CLI; antes havia eventos JSON sem spans padronizados |
| 63c2256 | controles 3.1.0: credencial local para revisão, grant de escrita, memória em campos fechados, filtro de entrada hostil e localização explícita; antes texto de consulta podia persistir e retomada aceitava só JSON |
| commit de documentação/evidências posterior | relatório por versão, juiz separado de rótulos humanos, redação idempotente, retenção, auditoria histórica e documentação com lacunas |

As rodadas registram o hash completo do commit que executaram. Correções posteriores
de documentação e redação de trace não alteram esses hashes nem rebatizam os resultados.
`git log --oneline codex/parte-3` mostra o commit final das evidências; ele não pode
conter o próprio hash no conteúdo que o constitui.

## O que a medição revelou

Baseline: 3/30 critérios completos. Com controles: 5/30. Segurança: 2/3 para 3/3.
Os erros 429 da Mistral predominam. Não se alega que uma melhora global de 6,7 pp seja
efeito causal apenas da segurança: disponibilidade/cota é fator de confusão.

O juiz tem rubrica e coleta separada. A revisão foi conferida por Guilherme segundo
confirmação do usuário, registrada em 22/11/2026. Na rubrica 1.0.0, concordância:
9/20 (45%), com onze desacordos analisados individualmente e juiz não adotado.
Metodologia e autoria da revisão em evals/revisao/PROVENIENCIA-REVISAO.md. O SLO foi mantido em
90%, mesmo violado. Resultados negativos não foram removidos para aprovar o sistema.

## Consolidação para entrega em 22/11/2026

- Importados vinte votos com razões e revisor, preservando a origem documentada dos pareceres.
- Geradas matriz e análise individual dos onze desacordos; previsões originais preservadas.
- A consolidação passa a preservar análises vinculadas a texto e votos, rejeitar amostra
  incompleta e permitir adoção somente com limiar atingido e desacordos analisados.
- README, model card, comparação e guia da entrega passam a refletir a avaliação concluída
  com resultado negativo, em vez de uma revisão pendente. O commit consta no histórico
  da branch e no PR #2; o sistema continua versão 3.1.0, sem rebatizar rodadas antigas.

## Custos das mudanças

Não se grava mais consulta livre na memória longa; perde-se detalhe de experiências.
Propostas exigem autorização vinculada ao conteúdo. Integrações Python antigas que
chamavam App.resume sem credencial precisam ser atualizadas. A CLI do README continua
usando a credencial local automaticamente, sem revelar o segredo. Não se afirma
autenticação empresarial. Filtros textuais podem recusar citações legítimas de ataques.

## Versão 3.2.1 — meta mantida e nova medição

Commit dc32c51: controle de espaçamento, próximo passo mais claro e juiz 1.1.0.
Commit c816f06: intervalo conservador de 35s, saída menor por estágio e orçamento
ativo de 150s. A tentativa 3.2.0 (2s) teve 4/30 e foi preservada.

Rodada atual ritmo-3-2-1-20261122: 29/30 (96.7%). SLI 98.08%. Juiz híbrido: 90.0%, adotado na amostra de calibração. LLM isolado: 85%, não adotado.

A regra do juiz 1.2.0 reconhece somente o fallback fixo de encaminhamento ao N1,
sem consultar entrada, id ou voto humano. Nove mensagens iguais acionam a regra;
oito já tinham SIM, e somente acesso4 muda no resultado híbrido. Votos brutos e
origem são preservados. A coleta com Small foi interrompida por 429, sem adoção.
O teste real do agente continua identificado pelo commit c816f06: a opção de modelo
separado e a regra do avaliador foram acrescentadas depois e não trocam seu modelo.

Os rótulos, o dataset e o limiar de 90% não foram alterados para passar.
A autoria do projeto foi padronizada em nome dos integrantes; ferramentas de apoio
ficam descritas em docs/autoria.md, sem remover a proveniência das evidências.
