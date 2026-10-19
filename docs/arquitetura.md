# Arquitetura — Parte 2

Desenho inicial da implementação (o inventário do grafo será acrescentado após execução).

```text
START -> interpretar [modelo: texto -> intenção, consulta, lacunas]
           | incompleto/ambíguo/fora do escopo -> finalizar
           | atendível
           v
         recuperar [código: corpus vigente + cadastro + memória]
           v
         responder [modelo: decisão sustentada por fontes]
           v
         validar [código: schema, fontes, orçamento, repetição]
           | corrigível uma vez -> responder
           | recusa/erro/informativo -> finalizar
           | proposta de registro
           v
         aprovar [INTERRUPT: analista N1; prazo de 24 horas]
           | rejeitado/expirado -> finalizar
           | aprovado ou editado
           v
         registrar [código: transação idempotente + memória] -> finalizar -> END
```

Autonomia: workflow com roteador semântico, e não agente de laço livre.
O julgamento do modelo em `interpretar` distingue falha, pedido informativo,
relato insuficiente e assunto externo. Um formulário determinístico não atende
ao contrato de texto livre. A consulta é uma etapa fixa somente para entradas
atendíveis; não se dá ao modelo autorização para escrever. O segundo laço é
avaliador-otimizador limitado a uma correção de saída, não planejamento livre.

Ferramentas: corpus e cadastro são leitura; registro e memória são escrita local
em SQLite. Não se altera conta, senha, rede ou sistema externo. Todo registro
aguarda analista N1; informações não geram registro. A pausa sobrevive ao processo.
Expiração nunca autoriza a escrita; a rotina `expirar` encerra as pendências vencidas.
<!-- GERADO -->

## Conferência executada

`python conferir_grafo.py`

```text
NÓS
__end__
__start__
aprovar
finalizar
interpretar
recuperar
registrar
responder
validar
ARESTAS
__start__ -> interpretar
aprovar -> finalizar [condicional]
aprovar -> registrar [condicional]
finalizar -> __end__
interpretar -> finalizar [condicional]
interpretar -> recuperar [condicional]
recuperar -> responder
registrar -> finalizar
responder -> finalizar [condicional]
responder -> validar [condicional]
validar -> aprovar [condicional]
validar -> finalizar [condicional]
validar -> responder [condicional]
```

## Campos do estado

| Campo | Tipo | Escreve | Lê / origem |
|---|---|---|---|
| owner | `<class 'str'>` | entrada | nós posteriores e checkpoint; definição em src/graph.py |
| thread_id | `<class 'str'>` | entrada | nós posteriores e checkpoint; definição em src/graph.py |
| text | `<class 'str'>` | entrada | nós posteriores e checkpoint; definição em src/graph.py |
| history | `Annotated[list[str], <function history_reducer at 0x000002345063BA60>]` | entrada | nós posteriores e checkpoint; definição em src/graph.py |
| started | `<class 'float'>` | entrada | nós posteriores e checkpoint; definição em src/graph.py |
| deadline | `<class 'float'>` | validar | nós posteriores e checkpoint; definição em src/graph.py |
| interpretation | `<class 'dict'>` | interpretar | nós posteriores e checkpoint; definição em src/graph.py |
| sources | `list[dict]` | recuperar | nós posteriores e checkpoint; definição em src/graph.py |
| tool_errors | `list[dict]` | recuperar | nós posteriores e checkpoint; definição em src/graph.py |
| memories | `list[dict]` | recuperar | nós posteriores e checkpoint; definição em src/graph.py |
| semantic | `<class 'dict'>` | recuperar | nós posteriores e checkpoint; definição em src/graph.py |
| decision | `<class 'dict'>` | interpretar/responder/validar/aprovar | nós posteriores e checkpoint; definição em src/graph.py |
| validation | `list[str]` | validar | nós posteriores e checkpoint; definição em src/graph.py |
| attempts | `<class 'int'>` | responder | nós posteriores e checkpoint; definição em src/graph.py |
| calls | `<class 'int'>` | interpretar/responder | nós posteriores e checkpoint; definição em src/graph.py |
| tokens | `<class 'int'>` | interpretar/responder | nós posteriores e checkpoint; definição em src/graph.py |
| signatures | `Annotated[list[str], <built-in function add>]` | validar | nós posteriores e checkpoint; definição em src/graph.py |
| events | `Annotated[list[dict], <built-in function add>]` | entrada e nós | nós posteriores e checkpoint; definição em src/graph.py |
| route | `<class 'str'>` | nós de decisão | nós posteriores e checkpoint; definição em src/graph.py |
| reason | `<class 'str'>` | interpretar/responder/validar/aprovar/registrar | nós posteriores e checkpoint; definição em src/graph.py |
| receipt | `<class 'dict'>` | registrar | nós posteriores e checkpoint; definição em src/graph.py |
| output | `<class 'dict'>` | finalizar | nós posteriores e checkpoint; definição em src/graph.py |

Escritas múltiplas são sequenciais: não há ramos paralelos no agente.
`events` e `signatures` usam concatenação; `history` concatena e mantém quatro mensagens.
Demais campos substituem o valor anterior. Sem reducer, eventos sequenciais se perdem.
A demonstração paralela da versão instalada levanta InvalidUpdateError, contrariando a hipótese de perda silenciosa do enunciado.

## O que o framework não forneceu

| Responsabilidade | Método | Linhas físicas |
|---|---|---|
| call | src/graph.py:86 | 24 |
| validar | src/graph.py:146 | 27 |
| aprovar | src/graph.py:174 | 19 |
| resume | src/graph.py:248 | 15 |

Contagem inclui assinaturas e comentários; esses métodos também fazem outras tarefas.
Motivo de término é campo próprio; detector compara hashes de decisões inválidas, sem aguardar recursion_limit.
Tetos explícitos: 90s de tempo ativo, 3 chamadas ao modelo, 12000 tokens contabilizados e 16 superpassos.
Tokens são teto observado após chamada, com saída limitada a 1200; não é um limite de cobrança estrito.
Timeout por chamada <=30s e retries=0; tempo de espera humana não conta como execução ativa.
Registro inexistente é recuperável e volta ao modelo como dado; API indisponível termina com erro_modelo.
Falhas inesperadas de armazenamento são fatais e podem exigir diagnóstico; não há repetição automática de escritas.

Decisão convertida em parâmetro: recursion_limit=16 e retries=0 são fixados explicitamente.
Alterar padrão de biblioteca não aumenta silenciosamente o orçamento. Versões estão fixadas em requirements.txt.

## Padrões e bifurcações

| Padrão | Onde | Justificativa / quando não usar |
|---|---|---|
| Sequencial com portão | responder -> validar | impede ação com fonte inválida; não se aplica à entrada já recusada |
| Router | interpretar -> recuperar/finalizar | texto livre exige modelo; código aplica o enum da rota |
| Avaliador-otimizador | validar -> responder, uma vez | erro verificável pode ser corrigido; repetição encerra |
| Paralelização, orquestrador e agente livre | não usados | tarefas curtas com dependências e ação bem definida |

Toda aresta condicional é aplicada por código. Só intenção e suficiência são propostas pelo modelo com schema;
o portão verifica fontes e invariantes. Aprovação vem da pessoa e expiração do relógio.

## Fora do estado

Histórico guarda texto conversacional; decisões e contadores têm campos próprios.
Não se guardam cliente OpenAI, conexão SQLite, API key, índice do corpus nem custo monetário estimado.
Hash de idempotência, score lexical e duração são derivados. Há um único agente; nenhum contrato entre agentes.

Términos: incompleto, ambiguo, fora_escopo, informativo, base_insuficiente, registrado, rejeitado,
aprovacao_expirada, laco_detectado, validacao_falhou, erro_modelo, limite_tempo, limite_chamadas,
limite_tokens e limite_orcamento. aguardando_aprovacao é suspensão, não conclusão.
