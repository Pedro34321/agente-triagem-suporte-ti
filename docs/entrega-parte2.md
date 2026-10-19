# Cobertura da Parte 2

| Item | Implementação | Evidência / situação |
|---|---|---|
| 0 Case | complemento em case.md | domínio simulado, limites e decisões declarados |
| 1 Entrada/saída | contracts.py + CLI | schema exportado; exemplos reais pendentes da API |
| 2 Prompts | src/prompts e prompts.md | hashes nos logs; experimento de ablação pronto, execução pendente |
| 3 Arquitetura | arquitetura.md | diagrama, rotas, orçamento, término e ferramentas |
| 4 RAG | knowledge.py | 10/10 no teste local; corpus revogado excluído |
| 5 Memória | storage.py | episódica, semântica, procedural; testes de contradição/decaimento/remoção |
| 6 Grafo | graph.py | StateGraph real, conferir_grafo.py e inventário |
| 7 Estado | State + reducers | tabela e demonstração sequencial/paralela |
| 8 HITL | interrupt/Command/SQLite | testes de reinício, edição, rejeição, expiração e duplicata |
| 9 Seis casos | scripts/demonstrar.py | nove casos preparados; execuções reais pendentes de créditos |
| 10 Projeto | README, requisitos fixos, .env.example | documentação versionável; nenhuma credencial incluída |

## O que falta antes da submissão

1. Regularizar saldo da API e executar `python -m scripts.demonstrar`.
2. Inspecionar cada saída: não basta produzir JSON válido. Confirmar categoria,
   recusa, divergência, ausência de registro informativo e uma única escrita no caso humano.
3. Executar `python -m scripts.ablacao`, revisar resultados e registrar a decisão sobre a frase.
4. Conferir os exemplos gerados em `docs/io.md` e README, e commitar as evidências.
5. Integrantes revisarem as regras simuladas do case e conseguirem explicar as escolhas.

Não declarar testes com double como validação do modelo. A medição RAG local usa
consultas rotuladas diretamente; o erro do roteador/reescrita pelo modelo não está nela.
MCP e multiagente são possibilidades da Parte 1, não requisitos implementados nesta entrega.
