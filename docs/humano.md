# Aprovação humana

O nó `aprovar` chama `interrupt`. Toda proposta de registro aguarda analista N1,
incluindo caso simples: optou-se por menor autonomia, pois a escrita altera a fila
simulada. É uma decisão mais conservadora que a Parte 1. Não existe ação sobre conta,
rede ou patrimônio. Consulta e orientação informativa não precisam dessa aprovação.

Payload inclui nome da ação, objeto completo, consequência, campos editáveis e prazo.
Prompt em `src/prompts/aprovacao.txt`. Respostas: aprovar, rejeitar ou editar prioridade
e encaminhamento. Pydantic valida enums e rejeita campos extras antes de retomar.
Categoria, fontes e texto não podem ser substituídos arbitrariamente na aprovação.

`Command(resume=...)` usa o mesmo thread_id. O nó reinicia antes do interrupt, portanto
não há escrita antes da pausa. SqliteSaver grava em arquivo e resiste ao fechamento
do processo. O grafo só encaminha para registrar após aprovação válida dentro do prazo.

Prazo: 24 horas. Após ele, qualquer retomada termina `aprovacao_expirada`. O comando
`python -m src.main expirar` varre pendências vencidas. Não há daemon instalado:
sem executar a rotina o registro pode continuar marcado pendente no banco, mas nenhuma
aprovação tardia consegue gravar. Para serviço contínuo, agendar essa rotina é tarefa
de implantação futura.

Chave de idempotência = SHA-256 de usuário, thread/caso e conteúdo aprovado canônico.
Restrição UNIQUE na tabela de triagens e INSERT OR IGNORE tornam replay seguro. Repetir
a chamada de retomada devolve o mesmo registro e `ja_existia=true`; também há teste
da ferramenta de escrita diretamente para cobrir falha entre transação e checkpoint.
Mesmo conteúdo em outro caso é outra ação legítima. Não se usa UUID aleatório como
substituto de hash de conteúdo.

Teste: `test_restart_edit_and_duplicate`, com fechamento/reabertura, edição da equipe,
duas aprovações e contagem igual a um. `test_no_write_on_rejection_or_timeout` prova
rejeição e silêncio. A demonstração real `caso_humano.json` é gerada por
`python -m scripts.demonstrar` quando a API estiver disponível; a aprovação nesse
script é roteirizada e explicitamente identificada, não autenticação de uma pessoa.
