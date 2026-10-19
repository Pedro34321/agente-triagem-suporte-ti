# Plano de prompt engineering — Parte 2

| Etapa | Técnica | Razão | Contrato | Teste |
|---|---|---|---|---|
| interpretar | few-shot + extração estruturada | distinguir falha de orientação e lacuna sem formulário | Interpretation, enums fechados, query <=300, patrimônio/local opcionais | nove casos do script; expectativa de rota e ausência de ids inventados |
| responder | grounding + few-shot + decomposição | decidir com corpus/cadastro recuperado | Decision, campos em `schema-decisao.json`, trecho literal e enum de categoria/prioridade/equipe | fontes existentes, não agir no informativo, recusar fora do corpus, coletar patrimônio inexistente |
| correção | feedback do validador, uma tentativa | corrigir citação ou violação detectável | mesmo Decision; proíbe referência nova sem fonte | double deliberadamente inválido deve terminar sem escrita |

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

## Regra da frase — experimento preparado

Frase candidata à ablação: `Não associe senha individual a rede coletiva.` no prompt
responder. Ela impede o erro observado na Parte 1. Comparar cinco relatos com e sem
a frase usando `python -m scripts.ablacao`. Critério: categoria, registro permitido,
fontes válidas e associação indevida de incidente. Sem créditos, **não há resultado**
experimental e a frase foi mantida. Não alegamos que encolher o prompt preservou
comportamento antes de medir. O script salva outputs e contagens dos dois tratamentos.
