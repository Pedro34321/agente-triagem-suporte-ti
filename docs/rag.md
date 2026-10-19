# Recuperação de conhecimento

Usamos **busca textual e consulta estruturada**, sem embeddings. O corpus é pequeno,
controlado, com termos técnicos explícitos; cadastro é consultado por chave exata.
Não se vende essa escolha como busca semântica: paráfrases sem palavras em comum
podem falhar. O modelo extrai assunto e consulta antes da busca; isso pode melhorar
sinônimos, mas também errar. Perguntas reais futuras devem ampliar a avaliação.

| Forma | Implementação | Uso |
|---|---|---|
| Textual | conjuntos de termos normalizados, filtro de assunto e vigência | procedimentos e exceções |
| Estruturada | SQLite com parâmetros; banco da Parte 1 aberto somente para leitura | patrimônio e incidente por localização |

Não há chunking nem k vetorial: cada documento é uma regra curta completa, incluindo
sua exceção. Todos os documentos pertinentes são entregues, sem recorte arbitrário.
O limite atual do corpus é sete documentos; ao crescer, será necessário medir janela
e reavaliar a recuperação. Não há grafo de conhecimento nem agregação neste contrato.

## Corpus e curadoria

`dados/corpus.json`: regras **simuladas pelo projeto**, não políticas de empresa real.
Responsáveis propostos pela manutenção: integrantes do grupo. Atualização por mudança
de procedimento, revisão a cada entrega. As fontes são lidas a cada execução; não há
índice persistente para reconstruir. `vigente=false` exclui KB-VPN-REVOGADO antes do
ranking. A versão antiga foi incluída deliberadamente: sem filtro ela aparece na
busca e recomenda uma prática incorreta. A recuperação sozinha não resolve vigência.

`dados/suporte.db`: equipamentos e incidentes fictícios da Parte 1. O registro de
novas triagens fica em outro banco, ignorado pelo Git, preservando a fonte de teste.

## Dez perguntas e evidências

`dados/perguntas_rag.json` contém a classificação de cada pergunta, fonte e trecho
esperado: sete textuais respondíveis, duas estruturadas e uma textual sem resposta.
Há três exceções: comprometimento de conta, VPN em equipamento pessoal e risco elétrico.
A avaliação reproduzível é `python -m scripts.avaliar_local`; resultados em
`logs/parte2/avaliacao-local.json`. Mede recuperação e trecho, não qualidade do LLM.

Quatro limitações observáveis: busca lexical pode perder sinônimos; documento revogado
exige curadoria; cadastro ausente exige coleta e não invenção; assunto externo exige
recusa. Consultar apenas documentos sem cadastro também não responderia onde está NB-10203.

## Integração ao grafo

Etapa fixa para relatos atendíveis: interpretar -> recuperar -> responder. Entradas
incompletas, ambíguas e externas terminam antes dela. Cada passagem registra
`chamadas_recuperacao=1`, ids e retornos de ferramenta. Correção de citação reutiliza
fontes já obtidas. O conjunto de logs reais deve permitir contar buscas sem resultado
e buscas inúteis. Na rodada final, seis das nove execuções fizeram uma busca; três
encerraram antes. A consulta fora do corpus retornou vazia e produziu recusa útil;
zero buscas foram desperdiçadas por repetição de correção. Não foi feita ablação
para estimar se alguma busca com resultado poderia ser eliminada sem perda.

O modelo seleciona ids; o código preenche o trecho com o texto integral da fonte curta.
O portão rejeita ids inexistentes e trechos que não são substrings exatas da fonte.
Isso verifica **existência da citação**, não prova que toda afirmação decorre dela.
Entailment e pertinência continuam sujeitos a revisão humana e avaliação rotulada.
