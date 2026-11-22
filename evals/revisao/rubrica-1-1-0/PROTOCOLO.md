# Protocolo de nova calibração — rubrica 1.1.0

Alvo declarado antes desta coleta: concordância mínima de **90%**, mantida de
evals/politica.json. Vinte casos, votos e notas já registrados em
evals/revisao/rotulos-humanos.json; não serão alterados para concordar com o juiz.

Mudança: instruções mais explícitas para aplicar o critério existente de utilidade
mínima. Classificação compreensível, pergunta útil ou encaminhamento explícito são
alternativas suficientes. O juiz não deve confundir resolução completa ou sucesso
da API com esse critério. O prompt de procedimento do agente de suporte deixa de
ser anexado à chamada de avaliação.

Prompt versionado: src/prompts/juiz.txt. As novas previsões serão coletadas pela API
e preservadas nesta pasta. O resultado anterior de 45% permanece em
evals/revisao/validacao-juiz.json, com seus onze desacordos e análise original.

Limitação: o prompt foi revisado após observar os erros nos mesmos vinte casos.
Esta é calibração sobre amostra conhecida, não teste cego nem estimativa independente
de desempenho futuro. Nova amostra com rótulos humanos independentes é necessária
para demonstrar generalização. A proveniência da revisão original não é alterada.
