# Memória implementada na Parte 2

O planejamento original foi preservado em `memoria-planejamento-parte1.md`.
Esta página descreve somente o código atual; diferenças são decisões explícitas.

| Estrutura | Escopo e finalidade | Persistência |
|---|---|---|
| Checkpoint | retomar conversa e aprovação, estado completo | `.runtime/checkpoints.sqlite`, SqliteSaver |
| Episódica | lembrar triagens aprovadas por similaridade lexical | tabela episodios e índice invertido termos |
| Semântica | lembrar cadastro previamente validado de equipamento, por chave | tabela fatos, índice owner/name/stamp |
| Procedural | regras estáveis aprovadas pelo mantenedor | `src/prompts/procedural.txt`, inserido no system prompt |
| RAG | consultar política e cadastro vigentes | corpus versionado e SQLite da Parte 1, externos à memória |

O checkpoint inclui relato, interpretação, evidências, proposta, prazo, contadores,
recibo e saída. O recibo e a chave UNIQUE permitem repetir um nó sem duplicar escrita.
Lembrar usa apenas dois episódios semelhantes do mesmo usuário; não serializa todos
os atendimentos no prompt. A similaridade Jaccard considera termos compartilhados,
com índice invertido para selecionar candidatos. Não há vetores ou API de embeddings.

## Escrita e contradição

Código escreve após aprovação: 0 ou 1 episódio com consulta curta, assunto, categoria,
prioridade e equipe; 0 ou 1 fato de equipamento consultado. Não guarda o relato completo
na memória longa nem aprende novas regras. Bytes por episódio aparecem no evento
`registrar.memoria.bytes`. O id é SHA-256 do conteúdo canônico e do proprietário;
fato inclui carimbo de tempo, pois observações novas têm validade diferente. Ambos
retornam `ja_existia`. Episódios idênticos reaproveitam o registro.

Na leitura de fato, ordenação decrescente por timestamp e desempate estável por hash.
`atual` e `descartados` são registrados no evento de recuperação; cadastro ao vivo
prevalece mesmo sobre a memória mais recente. Usuário não altera o cadastro por relato.

## Esquecimento implementado

Contradição mantém histórico e escolhe o mais novo. Decaimento rebaixa score por 0,25
após 90 dias; não elimina episódios aos 180 dias (isso ficou como proposta da Parte 1).
O corte representa mudança frequente de procedimentos, mas ainda precisa de validação
com dados reais. Remoção explícita por `python -m src.main esquecer USUARIO` elimina
episódios, termos, fatos, registros de triagem, associação de threads, checkpoints e
arquivos de logs operacionais das conversas desse usuário. Sem índice externo/cache.

Procedural e corpus são globais, curados e sem identificadores pessoais; não recebem
conteúdo de atendimentos. Dados e logs versionados são somente fixtures fictícias e
evidências sintéticas. Não há promessa de apagar histórico do Git, backups do sistema,
sincronização OneDrive ou registros do provedor. Nunca usar dados pessoais reais nesta
versão. A remoção é lógica e há VACUUM no banco de memória; não é apagamento forense.

O teste independente grava, observa recall, contradiz fato, remove e verifica recall,
dump SQL, logs e checkpoint. O teste não se limita a confiar no retorno de `forget`.

## Conversa e janela

Thread = usuário:sessão:caso. Mesmo identificador retoma o histórico; sessões/casos
diferentes isolam conversas simultâneas. Identidade é parâmetro da CLI local, **não
autenticação de produção**. Um caso registrado exige novo identificador para nova ação.

Reducer mantém as quatro mensagens mais recentes. A interpretação recebe histórico;
a resposta recebe o pedido atual, fontes e erros. Não há sumarização: detalhes antigos
se perdem. O limite de entrada é 2000 caracteres, consulta 300, resposta 1800, memória
recuperada dois episódios e três chamadas no máximo por turno. Ordem conceitual de
descarte: mensagens antigas primeiro; memórias já limitadas depois; nunca descartar
regras, evidência que sustenta a decisão ou pedido atual para esconder estouro.
O corpus curto é um pré-requisito: não há compactação automática para corpora grandes.

O checkpoint sobrevive ao término; eliminação precisa do comando explícito. Ao terminar,
somente triagem aprovada promove os campos selecionados à memória longa. Medições de
mudança na qualidade do modelo com memória estão pendentes de execução real.
