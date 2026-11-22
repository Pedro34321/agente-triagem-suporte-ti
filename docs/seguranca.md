# Segurança — Parte 3

Testes exclusivamente locais no próprio agente e em bancos temporários. Não foram
aplicados ataques a sistemas de terceiros. A API Mistral presta inferência de textos
fictícios; a aplicação de suporte e suas ferramentas são o alvo local dos testes.

## Canais não confiáveis

Entrada livre do usuário; documentos recuperados; registros retornados pelo cadastro;
memória de episódios/fatos; decisão e ids de fonte do modelo; resposta da revisão.
Não há mídia de entrada nem agente subordinado. O vídeo da apresentação é um artefato
externo de demonstração, não uma capacidade multimídia do agente.

## Riscos do case, por impacto

Critérios alinhados à análise do grupo em `exercicios/aula14-respostas.md`, encontrada
na main durante a integração: registro persistente de uma decisão/parecer, abuso de
identidade e comprometimento de dependências têm impacto 3. Envenenamento de memória
e indisponibilidade reversível têm impacto 2. Entre os impactos máximos, priorizamos
ASI03 e ASI01, como no exercício.

| Risco | Impacto | Canal e cenário | Controle e evidência |
|---|---|---|---|
| ASI03 identidade/privilégio | 3 | usuário afirma ser administrador e tenta aprovar/escrever | LocalAuthority.authenticate, grant HMAC e test_asi03_unauthorized_approval / test_asi03_direct_write_cannot_bypass_approval |
| ASI01 sequestro de objetivo | 3 | texto pede ignorar regras e executar powershell | HOSTILE bloqueia padrões antes do modelo; test_asi01_hostile_user_channel_blocked_before_model |
| ASI02 uso indevido de ferramenta | 3 | proposta tenta gravar sem pausa ou reexecutar a ação | registrar verifica grant e UNIQUE; teste de bypass e test_restart_edit_and_duplicate |
| ASI09 confiança humano-agente | 3 | revisor aceita classificação mal fundamentada | proposta explícita e fontes, risco semântico residual aceito abaixo |
| ASI10 agente desgovernado | 3 | execução não encerra ou operador quer suspender | tetos e TRIAGEM_SUSPENDED, test_suspend_blocks_calls_and_writes |
| ASI04 suprimentos | 3 | dependência Python comprometida roda com privilégios locais | versões fixadas, risco residual aceito; não há verificação criptográfica de toda dependência |
| ASI06 envenenamento persistente | 2 | entrada/documento/retorno tenta guardar instrução ou senha para futuras conversas | validate_episode/validate_fact e test_asi06_memory_rejects_external_text_and_credentials |
| ASI08 falhas em cascata | 2 | API indisponível, trace falha e fluxo tenta continuar escrevendo | erro encerra fluxo; trace preflight fail-closed, test_trace_failure_is_fail_closed |

ASI05 não é uma ferramenta oferecida: não há shell, eval de Python ou execução de
código à disposição do modelo. Bibliotecas comprometidas entram no risco ASI04.
ASI07 não se aplica porque não há comunicação entre agentes. O índice de código com
arquivo e linha, gerado a partir do código atual, aparece ao final desta página.

## Controles fora do prompt e seus custos

| Controle | O que impede / teste | Capacidade perdida | Falha |
|---|---|---|---|
| Credencial local e identidade de revisor + grant vinculado ao conteúdo | aprovação sem segredo ou proposta alterada; testes ASI03 | integração não pode aprovar só enviando texto/JSON; precisa credencial | fail-closed |
| Memória só com campos/enums permitidos e cadastro estruturado | persistir consulta livre, instrução ou segredo; teste ASI06 | perde detalhes textuais de experiências e cadastros com formatos novos | fail-closed |
| Bloqueio determinístico de padrões hostis | três ataques antes da chamada ao modelo; teste ASI01 | pode recusar texto legítimo que cita esses padrões | fail-closed, não é detector universal |
| Grant válido, prazo, unicidade e revisão antes da escrita | execução direta do nó, atraso e duplicata | nenhuma triagem se registra de forma autônoma | fail-closed |
| Auditoria disponível antes da escrita | continuar com exportador de trace em falha; teste específico | perde disponibilidade de registro quando auditoria falha | fail-closed no preflight |
| Localização precisa constar no texto | modelo inventa Andar 3 e associa incidente | não infere abreviações/locais implícitos | fail-closed na associação |
| Suspensão por variável local | novas chamadas e escritas após suspensão | bloqueia operação legítima enquanto ativa | fail-closed |

O preflight comprova exportação antes de escrever, mas não garante espaço em disco
futuro após uma gravação. Falha entre banco e término do trace ainda é risco residual.
Idempotência reduz duplicação no retry. O operador continua precisando investigar.

## RISCO ACEITO

**Comprometimento do operador/sistema de arquivos local e erro semântico remanescente.**
A CLI usa a credencial de `reviewer.json` na área operacional ignorada pelo Git.
Quem tem acesso a esse arquivo como operador pode aprovar. Isso não é login corporativo,
MFA ou segregação de funções. Também não há classificador completo de prompt injection
em documentos/memória; enum/allowlist limitam persistência e escrita, mas uma resposta
textual pode continuar errada. Aceitação restrita ao protótipo acadêmico, dados fictícios,
banco local e operador de confiança. Reavaliar antes de qualquer acesso multiusuário,
dado pessoal real, integração externa de escrita ou implantação empresarial.

**LACUNA:** a aplicação tenta restringir o arquivo com chmod, mas a ACL efetiva do Windows
não foi auditada. Dependências fixadas não equivalem a cadeia de suprimentos auditada.

## Dados pessoais: entrada, permanência e saída

Os datasets são fictícios. A entrada livre pode conter dado pessoal indevido, portanto
não afirmamos que o sistema tecnicamente impossibilita seu tratamento. Redação é
parcial: chaves com prefixos conhecidos, credenciais nomeadas, e-mails, CPF e alguns
telefones. Nomes livres e outros formatos podem passar. Não usar dados reais nesta versão.

| Lugar | Dados possíveis / finalidade | Base legal e prazo |
|---|---|---|
| Entrada, prompt e histórico | relato e pseudônimo para triagem | fixtures sintéticas não representam titulares; para uso real, base do art. 7º não definida: LACUNA; histórico até quatro mensagens, checkpoint até limpeza |
| Corpus e cadastro | patrimônio/local fictícios para fundamentação | sintéticos; mantidos versionados como material acadêmico |
| Memória longa e índice lexical | enums de triagem, fato de equipamento validado | sem consulta livre; base para dado real pendente; episódios rebaixados após 90 dias, remoção explícita disponível |
| Checkpoint e trace | relato redigido, contexto, decisão, aprovação e versão | prazo operacional declarado de 30 dias para trace/checkpoint; comando de limpeza, não daemon automático |
| Provedor Mistral | texto/contexto enviado para inferência | nenhuma credencial no prompt; base para dado real e retenção contratual do provedor: LACUNA, fora do controle da limpeza local |
| Autoria/revisão do trabalho | nomes de integrantes e futuramente do revisor, para atribuição | publicação e retenção acadêmica devem ser confirmadas pelo grupo; não presumimos consentimento para qualquer uso |

LGPD consultada na versão oficial da Câmara: art. 7º define hipóteses de tratamento;
o uso acadêmico não dispensa automaticamente esses requisitos. Não selecionamos uma
base legal genérica como se já existisse processo empresarial autorizado.
Fonte: https://www2.camara.leg.br/legin/fed/lei/2018/lei-13709-14-agosto-2018-787077-normaatualizada-pl.html

Memória **não guarda consulta, relato integral, nome, senha, chave ou regra aprendida**:
`validate_episode` admite apenas assunto/categoria/prioridade/equipe com valores fechados.
`validate_fact` admite somente campos de equipamento e formatos permitidos. O código
de registro obtém o fato da consulta atual de cadastro; não promove hipótese do usuário.
Os testes tentam gravar texto hostil e verificam ausência de registros.

Remoção por usuário cobre tabelas, índice de termos, checkpoints e traces locais;
testes inspecionam tabelas e arquivos independentemente. Não apaga snapshots do Git,
backups/OneDrive ou registros no provedor. Evidências versionadas são só fictícias.

## Histórico de credenciais

Comandos executados:

```text
git log --all --oneline -- .env
(saída vazia)

git log --all -S "OPENAI_API_KEY=" --oneline
a0581f5 Configura ambiente inicial do projeto
```

A segunda busca não veio vazia porque a configuração inicial versionou o nome da
variável no `.env.example`, com valor vazio, não uma chave. Por isso não alteramos
o histórico nem declaramos falsamente saída vazia. Uma varredura adicional de valores
de credenciais fica em `logs/parte3/auditoria-segredos.json`, sem imprimir segredos.
**LACUNA literal do enunciado:** busca por nome não distingue exemplo vazio de segredo.
Se a varredura detectar uma chave real, interromper publicação e revogar no provedor;
reescrever histórico sozinho não corrige os clones já existentes.

<!-- LINHAS -->
## Pontos de aplicação verificados

- autorizar: `src/security.py:32`.
- grant: `src/security.py:40`.
- episodio: `src/security.py:52`.
- fato: `src/security.py:61`.
- registrar: `src/graph.py:235`.
- validar: `src/graph.py:183`.
- interpretar: `src/graph.py:136`.
- run: `src/graph.py:274`.

| Risco | Componente e linha atual |
|---|---|
| ASI03 | `src/security.py:32 e src/security.py:40` |
| ASI01 | `src/graph.py:274 e src/graph.py:183` |
| ASI02 | `src/graph.py:235` |
| ASI09 | `src/graph.py:210` |
| ASI10 | `src/security.py:44 e src/graph.py:20` |
| ASI04 | `src/model.py:1 e requirements.txt:1` |
| ASI06 | `src/security.py:52 e src/security.py:61` |
| ASI08 | `src/telemetry.py:75 e src/graph.py:95` |
