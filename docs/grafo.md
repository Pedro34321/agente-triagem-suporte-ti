# Grafo da Parte 2

O desenho ASCII, inventário executado, padrões, campos, reducers e contagem de linhas
estão centralizados em [arquitetura.md](arquitetura.md), evitando dois diagramas divergentes.

Conferir: `python conferir_grafo.py`. Atualizar tabelas: `python -m scripts.documentar_grafo`.
Ambos importam `get_app().graph`, o mesmo objeto compilado e cacheado que a CLI usa.
Não remontam um grafo de exemplo para fingir a conferência.

`python -m scripts.avaliar_local` inclui microexperimento separado e rotulado de reducers.
Sequencial sem reducer mantém apenas b; com concatenação mantém a e b. Paralelo sem
reducer, nesta versão do LangGraph, levanta InvalidUpdateError. O agente principal
não usa paralelismo, portanto não afirma ganho de latência paralela.

Limites não substituem detector: duas decisões inválidas iguais produzem laco_detectado.
O recursion_limit é defesa adicional caso uma mudança crie um ciclo acidental.
