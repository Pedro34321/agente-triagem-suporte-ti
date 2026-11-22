# Model card — Agente de triagem de suporte de TI

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
| Escopo de triagem e bloqueio de padrões hostis | código `src/graph.py:274`, testes ASI01 |
| Aprovação com credencial local e identidade vinculada | `src/security.py:32`, test_asi03_unauthorized_approval |
| Escrita vinculada à proposta, prazo e aprovação | `src/security.py:40` e `src/graph.py:235`, teste de bypass |
| Até 3 chamadas de estágio, 90s, 12000 tokens observados, 16 superpassos | src/graph.py constantes e call; tokens não são teto rígido de fatura |
| Na falha de fonte/controle, não escrever | `src/graph.py:183`, testes de fonte inválida e auditoria indisponível |
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
Juiz: concordância 45% (9/20), limiar 90%, não adotado. 11 desacordos, todos analisados. Fonte: evals/revisao/validacao-juiz.json; matriz em docs/evals.md. Revisão assistida por IA, conferida por Guilherme segundo confirmação do usuário; proveniência em evals/revisao/PROVENIENCIA-REVISAO.md.

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
- `evals/resultados/controles-3-1-0/traces/simples/91c19d339e2321464d33b1154053fe07.jsonl`
- `evals/resultados/controles-3-1-0/traces/simples/e093a33ea772961ba6b0fd31d0537e07.jsonl`
- `evals/resultados/controles-3-1-0/traces/simples/f5699d954acce19f3dcaf0757fe918c8.jsonl`

A raiz de início identifica versão `3.1.0`,
modelo `ministral-8b-2512` e prompts por hash. Seu evento
decision_record contém a entrada redigida e a interpretação. Os spans de recuperação
e o contexto trazem as fontes KB-ACESSO.
A proposta foi `Acesso / Conta`, prioridade `Média`,
equipe `Suporte N1`, com término `aguardando_aprovacao`.
Na retomada, o evento approval atribui a decisão ao principal `revisor-local`,
timestamp Unix `1794611893.2640002`, resposta `{'decisao': 'aprovar', 'encaminhamento': None, 'prioridade': None}` e proposta completa.
O execute_tool registrar_triagem registra argumentos e recibo. A saída confirmou
registro `1`. As invocações são correlacionadas pelo mesmo
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
