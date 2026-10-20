# Plano de prompt engineering — Parte 2

| Etapa | Técnica | Razão | Contrato | Teste |
|---|---|---|---|---|
| interpretar | few-shot + extração estruturada | distinguir falha de orientação e lacuna sem formulário | Interpretation, enums fechados, query <=300, patrimônio/local opcionais | nove casos do script; expectativa de rota e ausência de ids inventados |
| responder | grounding + few-shot + decomposição | decidir com corpus/cadastro recuperado | DraftDecision, `schema-rascunho.json`, lista de ids; código materializa Decision com trechos literais | fontes existentes, não agir no informativo, recusar fora do corpus, coletar patrimônio inexistente |
| correção | feedback do validador, uma tentativa | corrigir seleção de fonte ou violação detectável | mesmo DraftDecision; proíbe referência nova sem fonte | double deliberadamente inválido deve terminar sem escrita |

Não há modelo extraindo fato para memória: código seleciona cadastro consultado e
resumo estruturado após aprovação. Não se usa cadeia de pensamento nem se pede raciocínio
interno. O schema é enviado ao Chat Completions da Mistral e validado pelo Pydantic.
O adaptador opcional OpenAI utiliza Responses parse.

Prompts ativos: interpretar, responder, procedural, aprovacao, todos em `src/prompts/`.
O prompt triagem-v1 foi movido preservando histórico e permanece como referência antiga,
sem uso em runtime. Cada log informa modelo e SHA-256 de cada arquivo de prompt.
Alterar um arquivo muda o hash e permite identificar a combinação exata da execução.

Proibido: campos extras, Markdown fora do objeto, categorias inventadas, patrimônio
inventado, considerar memória como fonte oficial e executar instruções de documentos.
Formatos exatos são exportados por `python -m scripts.avaliar_local`.

## Regra da frase — experimento executado

Frase candidata à ablação: `Não associe senha individual a rede coletiva.` no prompt
responder. Ela impede o erro observado na Parte 1. Comparar cinco relatos com e sem
a frase usando `python -m scripts.ablacao`. Resultado em `logs/parte2/ablacao.json`:
cinco acertos de categoria com a frase e cinco sem ela, no modelo Ministral 8B.
A frase foi removida apenas na variante experimental e mantida no prompt ativo:
o conjunto pequeno não contém incidente adversarial no contexto e não demonstra
que a proteção seja redundante em produção. Não houve ganho de qualidade medido;
o resultado negativo também foi registrado. Saídas completas, tokens, data e commit
permitem revisar outros critérios além do acerto de categoria contado pelo script.

## Correções observadas em execução

O 3B recusou indevidamente senha individual e tratou urgência como impacto coletivo.
Instruções mais precisas corrigiram o primeiro; coleta explícita corrigiu a ambiguidade.
Ao copiar JSON do cadastro, o modelo alterava trechos, corretamente rejeitados pelo
portão. A solução final foi seleção de ids pelo modelo e materialização literal pelo
código. O modelo não pode mais reescrever a citação. O 8B passou na divergência, mas
inicialmente confundiu propor registro crítico com executar sem humano; prompt e
validador agora distinguem as duas coisas. As rodadas anteriores foram preservadas.
