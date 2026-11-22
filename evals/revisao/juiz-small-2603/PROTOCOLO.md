# Protocolo — juiz Mistral Small 2603

Alvo mantido: concordância mínima de **90%** com os mesmos vinte rótulos, notas e
revisor registrados. Não alterar votos para obter aprovação. Mesma rubrica 1.1.0
em src/prompts/juiz.txt e mesmo critério de utilidade mínima.

Mudança isolada desta coleta: modelo do juiz de ministral-8b-2512 para
**mistral-small-2603**, com reasoning_effort=none. O modelo foi listado pela API da
conta e suporta saída estruturada. O agente continua usando ministral-8b-2512;
não se substitui nem rebatiza a rodada de 29/30 casos do agente.

A coleta anterior do juiz 8B, com a mesma rubrica 1.1.0, permanece em
evals/revisao/rubrica-1-1-0. A rubrica 1.0.0 e seus 45% permanecem em evals/revisao/.
Todas as tentativas serão preservadas, inclusive desacordos e erros de API.

O modelo foi escolhido após observar inconsistências na amostra conhecida. A medição
é calibração, sem avaliação cega ou validação de generalização. Proveniência dos
rótulos em evals/revisao/PROVENIENCIA-REVISAO.md. Adoção apenas se atingir 90% e todos
os desacordos forem analisados individualmente.

Fontes oficiais consultadas em 22/11/2026:

- [Modelo e saídas estruturadas](https://docs.mistral.ai/models/mistral-small-4-0-26-03).
- [Controle de reasoning_effort](https://docs.mistral.ai/inference/conversations/reasoning).

A tabela do modelo informa US$0,15/milhão de tokens de entrada e US$0,60/milhão de
saída na consulta. A estimativa do custo do agente mantém sua tabela própria;
as chamadas do juiz não integram o SLI nem o custo por execução do agente.
