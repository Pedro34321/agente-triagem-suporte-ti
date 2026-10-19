# Cobertura da Parte 2

| Item | Implementação | Evidência / situação |
|---|---|---|
| 0 Case | complemento em case.md | domínio simulado, limites e decisões declarados |
| 1 Entrada/saída | contracts.py + CLI | schemas exportados; nove exemplos reais em io.md |
| 2 Prompts | src/prompts e prompts.md | hashes nos logs; ablação executada, 5/5 com e sem frase |
| 3 Arquitetura | arquitetura.md | diagrama, rotas, orçamento, término e ferramentas |
| 4 RAG | knowledge.py | 10/10 no teste local; corpus revogado excluído |
| 5 Memória | storage.py | episódica, semântica, procedural; testes de contradição/decaimento/remoção |
| 6 Grafo | graph.py | StateGraph real, conferir_grafo.py e inventário |
| 7 Estado | State + reducers | tabela e demonstração sequencial/paralela |
| 8 HITL | interrupt/Command/SQLite | testes de reinício, edição, rejeição, expiração e duplicata |
| 9 Seis casos | scripts/demonstrar.py | nove casos reais; critérios 9/9, inclusive edição efetiva e duplicata |
| 10 Projeto | README, requisitos fixos, .env.example | documentação versionável; nenhuma credencial incluída |

## Revisão do grupo antes da submissão

1. Ler os exemplos e a arquitetura para explicar as decisões na apresentação.
2. Inspecionar cada saída: não basta produzir JSON válido. Confirmar categoria,
   recusa, divergência, ausência de registro informativo e uma única escrita no caso humano.
3. Revisar os resultados de ablação e a decisão conservadora de manter a frase.
4. Conferir os exemplos gerados em `docs/io.md` e README e revisar o pull request.
5. Integrantes revisarem as regras simuladas do case e conseguirem explicar as escolhas.

Não declarar testes com double como validação do modelo. A medição RAG local usa
consultas rotuladas diretamente; o erro do roteador/reescrita pelo modelo não está nela.
MCP e multiagente são possibilidades da Parte 1, não requisitos implementados nesta entrega.
OpenAI foi testado, mas o saldo estava esgotado. O provedor final é Mistral, autorizado
pelo usuário. Não há pendência de créditos OpenAI para executar esta versão.
