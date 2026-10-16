# Model Card — Agente de Triagem de Suporte de TI

**Versão do documento:** 1.0  
**Data:** 16/10/2026  
**Sistema:** Agente de Triagem de Suporte de TI  
**Repositório:** `agente-triagem-suporte-ti`

---

# 1. Identificação

## Afirmação

O sistema documentado neste model card é um protótipo acadêmico de um
**Agente de Triagem de Suporte de TI**.

O agente recebe um relato de suporte, interpreta a situação, pode consultar
informações auxiliares e produz uma classificação contendo, conforme o caso:

- categoria;
- prioridade;
- encaminhamento;
- justificativa;
- indicação de necessidade de intervenção humana.

A implementação principal está escrita em Python.

O agente não foi projetado como ferramenta autônoma de administração de
infraestrutura. Sua finalidade é realizar a triagem inicial e direcionar o caso.

## Evidências

- `README.md`
- `src/main.py`
- `prompts/triagem-v1.txt`
- `docs/case.md`
- `docs/arquitetura-v1.md`

No código principal, o objetivo da execução é registrado como:

`realizar triagem inicial de suporte`

Evidência:

- `src/main.py`, função `executar_agente`.

---

# 2. Finalidade

## Afirmação

A finalidade do agente é apoiar a triagem inicial de chamados de suporte de TI,
reduzindo o trabalho manual necessário para identificar o tipo de problema,
a prioridade e a equipe mais adequada para o atendimento.

O agente pode:

1. interpretar o relato do usuário;
2. classificar o chamado;
3. consultar informações sobre equipamentos;
4. consultar incidentes ativos;
5. consultar regras de triagem;
6. registrar uma triagem quando houver informação suficiente;
7. indicar quando o caso deve ser encaminhado para análise humana.

O agente não deve realizar diagnóstico técnico definitivo nem executar
alterações críticas em contas, redes, sistemas ou equipamentos.

## Evidências

A finalidade está definida no prompt:

- `prompts/triagem-v1.txt`, linhas 5 a 17 aproximadamente.

O prompt declara explicitamente:

> Você NÃO é responsável por diagnosticar definitivamente a causa técnica nem
> executar alterações críticas em sistemas, contas, redes ou equipamentos.

Evidência adicional:

- `prompts/triagem-v1.txt`, linha 10;
- `src/main.py`, conjunto `TOOLS`.

---

# 3. Autoridade

A autoridade do agente é limitada à triagem inicial e às ferramentas
explicitamente disponibilizadas pela aplicação.

## 3.1 Matriz de autoridade

| Limite | Regra atual | Onde é aplicado | Evidência | Situação |
|---|---|---|---|---|
| Escopo | realizar somente triagem inicial | prompt + conjunto de ferramentas | `prompts/triagem-v1.txt`; `src/main.py` | implementado parcialmente |
| Alterar senha | proibido | ausência de ferramenta | `src/main.py`, definição de `TOOLS` | aplicado |
| Bloquear/desbloquear conta | proibido | ausência de ferramenta | `src/main.py`, definição de `TOOLS` | aplicado |
| Alterar rede | proibido | ausência de ferramenta | `src/main.py`, definição de `TOOLS` | aplicado |
| Instalar software | proibido | ausência de ferramenta | `src/main.py`, definição de `TOOLS` | aplicado |
| Alterar equipamento | proibido | ausência de ferramenta | `src/main.py`, definição de `TOOLS` | aplicado |
| Consultar equipamento | permitido | ferramenta | `src/main.py`, linha 61; `src/tools.py`, linha 8 | aplicado |
| Consultar incidentes | permitido | ferramenta | `src/main.py`, linha 86; `src/tools.py`, linha 24 | aplicado |
| Consultar regras | permitido | ferramenta | `src/main.py`, linha 103; `src/tools.py`, linha 34 | aplicado |
| Registrar triagem | permitido | ferramenta de escrita | `src/main.py`, linha 117; `src/tools.py`, linha 60 | aplicado |
| Caso crítico deve ir para humano | obrigatório | prompt/regra retornada pela ferramenta | `prompts/triagem-v1.txt`, linha 34; `src/tools.py`, linha 50 | **LACUNA: não há bloqueio em código** |
| Limite de passos | máximo de 5 | código | `src/main.py`, linha 23 | aplicado |
| Orçamento de tokens | máximo lógico de 4.000 tokens acumulados | código | `src/main.py`, linha 24 | aplicado |
| Tempo de execução | máximo de 60 segundos | código | `src/main.py`, linha 25 | aplicado |
| Limite monetário | não definido | — | — | **LACUNA** |
| Suspensão administrativa | não definida formalmente | — | — | **LACUNA** |

---

## 3.2 Ferramentas disponíveis

O agente possui quatro ferramentas:

- `consultar_equipamento`;
- `consultar_incidentes`;
- `consultar_regras`;
- `registrar_triagem`.

Não existe ferramenta para:

- redefinir senhas;
- bloquear ou desbloquear contas;
- alterar configurações de rede;
- executar comandos em computadores;
- instalar software;
- excluir usuários;
- aprovar gastos;
- alterar dados cadastrais de pessoas.

Essa ausência de ferramentas funciona como um limite estrutural: ainda que o
modelo tente solicitar uma dessas ações, a aplicação não fornece uma ferramenta
capaz de realizá-la.

## Evidência

`src/main.py`, bloco `TOOLS`.

---

## 3.3 Credenciais e privilégios

A conexão com o modelo utiliza:

- `OPENAI_API_KEY`;
- `LLM_BASE_URL`;
- `LLM_MODEL`.

Evidência:

- `.env.example`, linhas 1 a 3;
- `src/main.py`, função `criar_cliente`.

A chave utilizada pelo provedor de modelo não aparece no repositório.

**LACUNA — prioridade alta:** o repositório não contém evidência sobre os
privilégios concedidos à chave real utilizada nos testes nem sobre restrições
configuradas na plataforma do provedor.

### Correção proposta

Documentar:

- tipo de credencial;
- ambiente ao qual ela dá acesso;
- modelos permitidos;
- limite de gasto;
- procedimento de revogação.

---

## 3.4 Credencial do banco

O protótipo utiliza SQLite em:

`dados/suporte.db`

O mesmo processo Python possui acesso de leitura e escrita ao arquivo.

Evidência:

- `src/database.py`, linha 5;
- `src/database.py`, funções `buscar_equipamento`,
  `buscar_incidentes_ativos` e `salvar_triagem`.

**LACUNA — prioridade alta:** não existe separação de privilégios entre uma
credencial somente de leitura e outra de escrita. No SQLite, o controle atual
depende do acesso ao arquivo.

### Correção proposta

Em produção, separar:

- serviço de consulta;
- serviço de gravação;
- permissões mínimas necessárias;
- usuário administrativo.

---

## 3.5 Limite de gasto e execução

O sistema possui limites técnicos:

- `MAX_PASSOS = 5`;
- `MAX_TOKENS = 4000`;
- `MAX_TEMPO = 60`.

Evidência:

- `src/main.py`, linhas 23 a 25.

Esses limites reduzem o risco de uma execução continuar indefinidamente.

Entretanto, eles **não são equivalentes a um limite monetário garantido pela
plataforma do provedor**.

**LACUNA — prioridade média:** não existe no repositório evidência de um limite
financeiro externo aplicado à chave do provedor.

---

## 3.6 Limiar de aprovação humana

O projeto determina que casos contraditórios, críticos ou que não possam ser
classificados com segurança devem ser encaminhados para um humano.

Evidência:

- `prompts/triagem-v1.txt`, linha 34;
- `src/tools.py`, regra `"Caso crítico deve ser encaminhado para humano."`.

Entretanto, esse requisito depende atualmente de instrução fornecida ao modelo.

Não existe uma condição em Python como:

```python
if prioridade == "Crítica":
    bloquear_decisao()
    exigir_aprovacao_humana()
```

Portanto:

**LACUNA — prioridade alta:** a aprovação humana para casos críticos é
controlada principalmente pelo prompt e não por uma barreira externa ao modelo.

### Correção proposta

Implementar verificação determinística antes do registro final:

```text
se prioridade == Crítica
        ↓
bloquear conclusão automática
        ↓
status = aguardando_revisao
        ↓
humano analisa
        ↓
aprovar ou corrigir
```

---

## 3.7 Comportamento quando um controle falha

Quando a chamada ao modelo gera exceção, a implementação retorna uma mensagem
informando que o caso deve seguir para análise humana.

Evidência:

- `src/main.py`, tratamento de exceção da chamada ao modelo, próximo à linha 256.

Entretanto, falhas das ferramentas são retornadas ao modelo como dados.

Evidência:

- `src/main.py`, função `executar_ferramenta`.

**LACUNA — prioridade média:** uma falha de ferramenta não força
deterministicamente o encerramento seguro da execução.

### Correção proposta

Definir quais ferramentas são críticas e, quando falharem, interromper a
decisão automática e exigir análise humana.

---

## 3.8 Quem pode suspender o agente

Atualmente o protótipo pode ser interrompido encerrando o processo ou removendo
a credencial utilizada pela aplicação.

Entretanto, não existe no repositório uma política formal identificando quem
possui autoridade para realizar essa suspensão.

**LACUNA — prioridade alta.**

### Correção proposta

Definir no ambiente operacional:

- responsável pelo serviço;
- responsável técnico;
- responsável pela chave;
- mecanismo de `kill switch`;
- procedimento de suspensão emergencial.

---

# 4. Ferramentas e integrações

## Afirmação

O agente utiliza ferramentas locais e uma integração externa com um provedor
compatível com o SDK OpenAI.

### Ferramentas internas

| Ferramenta | Acesso | Efeito |
|---|---|---|
| `consultar_equipamento` | banco SQLite | somente leitura |
| `consultar_incidentes` | banco SQLite | somente leitura |
| `consultar_regras` | regras no código | somente leitura |
| `registrar_triagem` | banco SQLite | escrita |

## Evidências

Implementação:

- `src/tools.py`
- `src/database.py`

Definição das ferramentas expostas ao modelo:

- `src/main.py`, bloco `TOOLS`.

---

## Integração externa

A aplicação cria um cliente utilizando a biblioteca `openai`.

O endereço da API pode ser configurado por:

`LLM_BASE_URL`

Isso permite utilizar um endpoint compatível com o SDK.

Evidências:

- `src/main.py`, função `criar_cliente`;
- `.env.example`.

**LACUNA:** o endpoint efetivamente usado não é registrado nos logs das
execuções.

---

# 5. Modelo e provedor

## Afirmação

O modelo efetivamente utilizado na implementação e nos testes documentados
desta versão foi:

`ministral-3b-2512`

A seleção é configurável pela variável:

`LLM_MODEL`

O valor padrão do código também é:

`ministral-3b-2512`

## Evidências

- `src/main.py`, função `executar_agente`, configuração de `LLM_MODEL`;
- `docs/modelos.md`, seção **Modelo utilizado na versão entregue**.

Durante o planejamento havia sido considerado o Mistral Small 4, mas a
implementação prática passou a utilizar `ministral-3b-2512`.

Evidência:

- `docs/modelos.md`.

A API foi acessada utilizando cliente compatível com o SDK OpenAI e endereço
configurável.

## Parâmetros observáveis

A chamada ao modelo utiliza:

```text
tool_choice = auto
max_tokens = 1000
temperature = 0.2
```

Evidência:

- `src/main.py`, chamada `cliente.chat.completions.create`, próxima à linha 247.

## Lacunas

**LACUNA — prioridade alta:** o log atual não persiste de maneira confiável,
para cada execução:

- versão exata do modelo;
- provedor;
- endpoint;
- versão do SDK;
- parâmetros completos;
- versão do prompt utilizada.

Sem esses dados, uma decisão histórica não pode ser reproduzida integralmente.

### Correção proposta

Adicionar ao registro de cada execução:

```json
{
  "execution_id": "...",
  "model": "ministral-3b-2512",
  "provider": "...",
  "prompt_version": "1.1",
  "temperature": 0.2,
  "max_tokens": 1000,
  "timestamp": "..."
}
```

---

# 6. Dados

## 6.1 Inventário

O protótipo pode tratar informações fornecidas diretamente pelo usuário e
informações disponíveis no banco local.

| Local | Dado possível | Finalidade | Base legal | Retenção atual | Evidência |
|---|---|---|---|---|---|
| relato enviado ao agente | texto livre do usuário | classificar o chamado | **LACUNA em produção** | **LACUNA** | `src/main.py` |
| tabela `equipamentos` | patrimônio, usuário, tipo, status e localização | identificar equipamento | **LACUNA em produção** | **LACUNA** | `dados/init_db.py`, linhas 13+ |
| tabela `incidentes` | título, categoria, localização, quantidade afetada e status | identificar incidentes coletivos | depende do conteúdo; **LACUNA** | **LACUNA** | `dados/init_db.py`, linhas 23+ |
| tabela `triagens` | relato, categoria, prioridade, encaminhamento, justificativa e flag humana | registrar resultado da triagem | **LACUNA em produção** | **LACUNA** | `dados/init_db.py`, linhas 34+ |
| contexto enviado ao LLM | relato + prompt + retornos de ferramentas usados na execução | produzir a triagem | **LACUNA em produção** | depende do provedor; **LACUNA** | `src/main.py` |
| logs de teste | resposta, trajetória, argumentos e resultados | depuração e avaliação | **LACUNA em produção** | **LACUNA** | pasta `logs/` |
| memória futura | fatos/episódios eventualmente persistidos | continuidade entre execuções | ainda não implementada | ainda não definido | `docs/memoria.md` |

---

## 6.2 Base legal

Os testes acadêmicos da Aula 12 utilizaram um titular inteiramente fictício:

`TITULAR_TESTE_LGPD_001`

Portanto, o teste de eliminação não representa tratamento de dados pessoais de
uma pessoa real.

Evidências:

- `scripts/teste_eliminacao_lgpd.py`;
- `evidencias/aula-12/saida-eliminacao.txt`.

Para uma eventual implantação com usuários reais:

**LACUNA — prioridade crítica:** o protótipo ainda não documenta qual hipótese
do artigo 7º da LGPD sustentaria cada finalidade de tratamento.

A organização controladora deverá definir formalmente a hipótese legal adequada
a cada finalidade antes do uso em produção, levando em consideração a relação
com os usuários e o contexto do serviço.

Não se assume neste documento uma hipótese legal sem decisão do controlador.

---

## 6.3 Dados que entram no contexto do modelo

O relato do usuário é adicionado diretamente às mensagens enviadas ao modelo.

Quando uma ferramenta é utilizada, o resultado da ferramenta também é
adicionado ao contexto.

Evidência:

- `src/main.py`, função `executar_agente`.

Assim, informações retornadas por `consultar_equipamento`, por exemplo, podem
ser enviadas ao provedor do modelo durante aquela execução.

**LACUNA — prioridade alta:** não existe etapa automática de minimização,
mascaramento ou remoção de dado pessoal antes do envio ao modelo.

### Correção proposta

Aplicar uma camada de minimização antes da criação das mensagens:

```text
entrada
  ↓
detecção de campos desnecessários
  ↓
mascaramento/pseudonimização
  ↓
contexto mínimo necessário
  ↓
modelo
```

---

## 6.4 Banco de equipamentos

A tabela `equipamentos` possui:

- patrimônio;
- usuário;
- tipo;
- status;
- localização.

Evidência:

- `dados/init_db.py`, a partir da linha 13.

A base de exemplo inclui nomes como:

- João Silva;
- Maria Souza;
- Carlos Santos.

Evidência:

- `dados/init_db.py`, registros de demonstração a partir da linha 51.

O repositório não informa se esses nomes são referentes a pessoas reais ou
apenas dados de exemplo.

**LACUNA:** classificar formalmente o conjunto de dados de demonstração e
garantir que somente dados fictícios ou adequadamente autorizados sejam
versionados.

---

## 6.5 Minimização

Há risco de duplicação de informação pessoal porque um nome ou identificador
pode aparecer em:

- cadastro do equipamento;
- relato;
- justificativa;
- log;
- contexto enviado ao modelo.

O exercício de eliminação demonstrou esse problema ao inserir o identificador
de teste tanto em `equipamentos` quanto em `triagens`.

Evidência:

- `evidencias/aula-12/saida-eliminacao.txt`.

**LACUNA — prioridade alta:** não há política automática de minimização para
texto livre.

---

# 7. Avaliação

## Afirmação

O projeto possui uma estratégia de avaliação definida na Aula 11.

O documento de avaliação especifica um golden dataset v1 e avalia o agente em
mais de um nível, evitando considerar somente a aparência da resposta final.

## Evidência

- `exercicios/aula-11-avaliacao.md`.

A avaliação considera propriedades relacionadas a:

- saída determinística;
- trajetória de ferramentas;
- resultado persistido;
- justificativa avaliada por juiz quando necessário.

Também foram preservados casos observados durante o desenvolvimento.

Entre os registros existentes estão casos como:

- caso simples;
- divergência;
- registro inexistente;
- solicitação que não deveria gerar incidente.

Evidência:

- pasta `logs/`;
- `docs/modelos.md`.

## Riscos de avaliação

Grande parte do conjunto inicial foi elaborada de forma sintética.

Isso já está reconhecido na documentação da Aula 11.

**LACUNA — prioridade média:** ainda não existe evidência de uma suíte
automatizada completa executada continuamente como portão de integração.

### Correção proposta

Implementar a suíte e impedir promoção de uma versão quando ocorrer regressão
acima dos limites definidos no documento de avaliação.

---

# 8. Limites conhecidos

Os principais limites conhecidos da versão atual são:

### 8.1 Associação incorreta de incidentes

Durante o desenvolvimento, o agente já associou um problema individual de
autenticação a um incidente coletivo sem evidência suficiente de
correspondência.

Esse comportamento motivou alterações no prompt e nas descrições das
ferramentas.

Evidências:

- `docs/modelos.md`;
- `prompts/triagem-v1.txt`;
- `logs/caso-divergencia.txt`.

---

### 8.2 Regras dependentes do modelo

Algumas regras importantes existem apenas no prompt.

Exemplo:

> casos críticos devem ser encaminhados para humano.

Como não existe uma barreira equivalente fora do modelo, a regra pode ser
desobedecida.

**LACUNA — prioridade alta.**

---

### 8.3 Informação insuficiente no registro

Os registros atuais não permitem reconstruir integralmente:

- versão exata do modelo;
- versão exata do prompt;
- índice utilizado;
- endpoint do provedor;
- identidade de eventual revisor humano.

Evidência:

- `evidencias/aula-12/decisao-reconstruida.md`.

---

### 8.4 Ausência de política de retenção

Não há no protótipo prazo formal de retenção para:

- triagens;
- logs;
- dados de equipamento;
- registros de revisão;
- registros de eliminação.

**LACUNA — prioridade alta.**

---

### 8.5 Memória ainda não implementada

Existe um projeto para memória de curto e longo prazo, mas as estruturas
persistentes descritas ainda não fazem parte do fluxo operacional atual.

Evidência:

- `docs/memoria.md`;
- `evidencias/aula-12/saida-eliminacao.txt`.

---

### 8.6 Não determinismo

O modelo utiliza geração probabilística, mesmo com `temperature = 0.2`.

Ferramentas e dados também podem mudar entre execuções.

Portanto, uma mesma entrada não possui garantia absoluta de produzir a mesma
saída no futuro.

Evidência:

- `src/main.py`;
- `exercicios/aula-11-avaliacao.md`.

---

# 9. Riscos aceitos

Esta versão acadêmica aceita temporariamente alguns riscos porque o sistema
ainda é um protótipo e não deve ser utilizado como agente autônomo de produção.

## Risco 1 — Classificação incorreta

O agente pode escolher categoria, prioridade ou encaminhamento incorretos.

Mitigação atual:

- regras de triagem;
- testes;
- possibilidade de indicação de humano.

Evidência:

- `prompts/triagem-v1.txt`;
- `exercicios/aula-11-avaliacao.md`.

---

## Risco 2 — Uso incorreto de ferramenta

O modelo pode consultar uma ferramenta desnecessária ou deixar de consultar uma
ferramenta necessária.

Mitigação:

- descrições restritivas nas ferramentas;
- regras no prompt;
- análise de trajetória.

Evidências:

- `src/main.py`;
- `prompts/triagem-v1.txt`;
- `exercicios/aula-11-avaliacao.md`.

---

## Risco 3 — Persistência de texto livre

O relato e a justificativa podem conter dados pessoais desnecessários.

Mitigação atual:

- nenhuma automática.

**LACUNA — prioridade alta.**

---

## Risco 4 — Registro duplicado

A função `registrar_triagem` grava uma nova linha no banco.

Não há evidência atual de uma chave de idempotência impedindo duplicação caso a
mesma ação seja executada novamente.

Evidência:

- `src/database.py`, função `salvar_triagem`.

**LACUNA — prioridade média.**

---

## Risco 5 — Dependência do provedor externo

Uma indisponibilidade do provedor impede a chamada ao modelo.

O código trata a falha e orienta encaminhamento humano.

Evidência:

- `src/main.py`.

---

# 10. Supervisão humana

## Afirmação

O projeto prevê intervenção humana em situações nas quais o agente não deve
concluir sozinho.

O prompt determina intervenção humana para casos:

- contraditórios;
- críticos;
- impossíveis de classificar com segurança.

Evidência:

- `prompts/triagem-v1.txt`, linha 34.

A estrutura de saída também possui:

`precisa_humano`

Evidências:

- `src/main.py`;
- `src/tools.py`;
- `dados/init_db.py`.

## Limitação

A decisão `precisa_humano = true` ainda é produzida pelo próprio modelo.

Não existe workflow implementado que pause a execução e espere uma pessoa
específica aprovar a decisão.

**LACUNA — prioridade alta.**

### Correção proposta

Criar estado:

`aguardando_revisao_humana`

e impedir gravação definitiva até que uma pessoa autorizada aprove ou altere o
resultado.

---

## Pedido de revisão

Foi documentado um procedimento de revisão de decisão automatizada utilizando
uma decisão registrada do protótipo.

Evidência:

- `evidencias/aula-12/revisao-lgpd.md`.

A explicação registra:

- classificação;
- prioridade;
- encaminhamento;
- ferramenta utilizada;
- critérios observados.

**LACUNA:** ainda não há identificação formal do papel ou pessoa que realizaria
a revisão em produção.

---

# 11. Registro e retenção

## 11.1 Registro atual

Durante a execução, o objeto `estado` armazena:

- objetivo;
- relato;
- quantidade de passos;
- tokens utilizados;
- trajetória das ferramentas;
- motivo de término.

Evidência:

- `src/main.py`, função `executar_agente`.

Para cada chamada de ferramenta, são registrados na trajetória:

- passo;
- nome da ferramenta;
- argumentos;
- resultado.

Evidência:

- `src/main.py`, região próxima à linha 294.

Isso permite observar parte do caminho utilizado pelo agente.

---

## 11.2 Reconstrução executada

Uma execução do protótipo foi reconstruída a partir de:

`logs/caso-divergencia.txt`

A reconstrução completa está em:

`evidencias/aula-12/decisao-reconstruida.md`

Foi possível identificar:

- decisão final;
- categoria;
- prioridade;
- encaminhamento;
- quantidade de passos;
- tokens registrados;
- ferramenta `consultar_incidentes`;
- resultado retornado por essa ferramenta.

Por outro lado, o registro não foi suficiente para comprovar integralmente:

- modelo exato;
- endpoint;
- versão do prompt carregado;
- índice ou versão de conhecimento;
- dados pessoais transmitidos ao provedor;
- identidade de um revisor humano.

Esses itens permanecem como lacunas.

---

## 11.3 Retenção

Não existe política de retenção formal implementada no protótipo.

**LACUNA — prioridade alta.**

Antes de produção devem ser definidos prazos distintos para:

- triagens operacionais;
- logs técnicos;
- evidências de auditoria;
- solicitações de titulares;
- registros de revisão;
- comprovação de eliminação.

A retenção deve ser definida conforme finalidade e obrigações aplicáveis, e não
simplesmente por prazo indefinido.

---

## 11.4 Eliminação

Foi executado um teste prático de eliminação utilizando um titular totalmente
fictício:

`TITULAR_TESTE_LGPD_001`

Antes da eliminação:

```text
equipamentos: 1
triagens: 1
```

Depois:

```text
equipamentos: 0
triagens: 0
```

Resultado:

```text
RESULTADO: APROVADO
```

Evidências:

- `scripts/teste_eliminacao_lgpd.py`;
- `evidencias/aula-12/eliminacao-lgpd.md`;
- `evidencias/aula-12/saida-eliminacao.txt`.

A verificação foi realizada em uma nova conexão após a operação de remoção.

O banco original não foi alterado; a avaliação utilizou uma cópia temporária.

---

## 11.5 Conflito entre eliminar e provar

O teste preservou a saída da execução como evidência.

Isso foi possível sem preservar dado pessoal real porque o identificador
utilizado era totalmente fictício.

Em produção, a evidência de atendimento de um pedido de eliminação deveria
guardar somente o mínimo necessário, por exemplo:

- ID do pedido;
- horário;
- estruturas verificadas;
- resultado;
- quantidade de registros removidos;
- responsável pelo procedimento.

Não seria apropriado recriar na própria evidência todos os dados que acabaram
de ser eliminados.

---

# 12. Histórico de mudanças

| Versão | Alteração | Evidência |
|---|---|---|
| arquitetura inicial | definição do fluxo do agente | `docs/arquitetura-v1.md` |
| Parte 1 | documentação do case | `docs/case.md` |
| seleção de modelos | análise e escolha inicial | `docs/modelos.md` |
| implementação prática | adoção de `ministral-3b-2512` | `docs/modelos.md`, `src/main.py` |
| prompt 1.1 | restrição do uso de incidentes e regras de segurança | `prompts/triagem-v1.txt` |
| projeto de memória | definição de curto/longo prazo e esquecimento | `docs/memoria.md` |
| Aula 11 | desenho do processo de avaliação | `exercicios/aula-11-avaliacao.md` |
| Aula 12 | reconstrução de decisão | `evidencias/aula-12/decisao-reconstruida.md` |
| Aula 12 | exercício de revisão | `evidencias/aula-12/revisao-lgpd.md` |
| Aula 12 | teste de eliminação | `evidencias/aula-12/eliminacao-lgpd.md` |
| Aula 12 | evidência executável da eliminação | `evidencias/aula-12/saida-eliminacao.txt` |
| 1.0 | criação deste model card | `docs/model-card.md` |

---

# 13. Reconstrução de uma decisão concreta

A decisão escolhida para auditoria é o caso registrado em:

`logs/caso-divergencia.txt`

A reconstrução detalhada está em:

`evidencias/aula-12/decisao-reconstruida.md`

## O que o registro permite responder

A decisão produziu:

- categoria `Rede / Conectividade`;
- prioridade `Alta`;
- encaminhamento `Suporte N2 (Equipe de Rede)`;
- `precisa_humano = false`.

A execução utilizou:

- 2 passos;
- 4065 tokens registrados;
- ferramenta `consultar_incidentes`.

A ferramenta retornou um incidente:

- indisponibilidade de rede;
- localização Andar 3;
- 35 usuários afetados;
- status ativo.

## O que o registro não permite responder

### Modelo exato da execução

**LACUNA.**

Embora a implementação atual utilize `ministral-3b-2512`, o registro histórico
analisado não contém um campo imutável com a versão do modelo utilizado naquela
execução.

### Versão do prompt

**LACUNA.**

O prompt atual possui versão `1.1`, mas a execução não registra um hash ou
versão imutável do prompt carregado.

### Índice

Não existe índice vetorial implementado nesse fluxo.

Entretanto, o registro também não possui um campo explícito indicando:

`index_version = none`

**LACUNA de rastreabilidade.**

### Contexto recuperado

Foi registrado o resultado de `consultar_incidentes`.

Isso permite recuperar parte do contexto utilizado.

### Ferramentas e argumentos

Foi registrada a ferramenta:

`consultar_incidentes`

com argumentos:

```json
{}
```

### Política vigente

As políticas podem ser inferidas do repositório atual, porém não há snapshot da
política anexado à execução.

**LACUNA.**

### Dados pessoais e destino

O registro atual não permite determinar com precisão todos os dados enviados ao
provedor naquela execução.

**LACUNA — prioridade alta.**

### Revisão humana

Não existe no registro identificação de revisor humano.

**LACUNA.**

---

# 14. Revisão de decisão automatizada

Foi produzido um exemplo de atendimento de revisão da decisão reconstruída.

Evidência:

`evidencias/aula-12/revisao-lgpd.md`

A explicação destinada ao titular apresenta:

- decisão produzida;
- critérios observados;
- consulta realizada;
- incidente utilizado;
- relação entre evidência e classificação.

O objetivo é permitir revisão sem revelar detalhes desnecessários ou segredos
de implementação.

**LACUNA:** o processo ainda não está implementado como funcionalidade
operacional nem há função formalmente designada para executar a revisão.

---

# 15. Eliminação de dados

O procedimento de eliminação foi efetivamente executado em dados fictícios.

O teste criou dados em uma cópia temporária do banco, verificou a presença,
executou a remoção e realizou uma nova consulta independente.

Evidências:

- `scripts/teste_eliminacao_lgpd.py`;
- `evidencias/aula-12/saida-eliminacao.txt`;
- `evidencias/aula-12/eliminacao-lgpd.md`.

Resultado:

```text
ANTES:
equipamentos = 1
triagens = 1

DEPOIS:
equipamentos = 0
triagens = 0

RESULTADO: APROVADO
```

O teste comprovou a eliminação nas estruturas avaliadas:

- `equipamentos`;
- `triagens`.

Não comprovou eliminação em:

- provedor externo;
- logs históricos de uma pessoa real;
- índice vetorial;
- memória de longo prazo.

Isso ocorre porque essas estruturas não participaram da execução de teste ou
ainda não estão implementadas.

---

# 16. Lacunas consolidadas

| ID | Lacuna | Prioridade | Correção proposta |
|---|---|---|---|
| L01 | regra de encaminhamento humano não possui bloqueio externo ao modelo | Alta | implementar gate determinístico |
| L02 | privilégios da credencial do LLM não estão documentados | Alta | registrar escopo, modelos, limite e revogação |
| L03 | SQLite não separa leitura e escrita por credenciais | Alta | migrar para controle de acesso apropriado em produção |
| L04 | não há limite monetário comprovado no provedor | Média | configurar e registrar limite externo |
| L05 | não existe responsável formal pelo `kill switch` | Alta | definir papel e procedimento de suspensão |
| L06 | falha de ferramenta não força sempre revisão humana | Média | classificar ferramentas críticas e aplicar fail-closed |
| L07 | versão exata do modelo não é registrada por execução | Alta | gravar modelo no registro |
| L08 | versão/hash do prompt não é registrada por execução | Alta | versionar e gravar hash |
| L09 | endpoint/provedor efetivo não é registrado por execução | Média | incluir metadado no trace |
| L10 | parâmetros completos não são registrados | Média | persistir parâmetros da chamada |
| L11 | hipótese legal de produção não está definida | Crítica | definir base legal por finalidade antes de produção |
| L12 | prazo de retenção não está definido | Alta | criar política de retenção |
| L13 | não existe minimização automática antes do envio ao LLM | Alta | mascarar e reduzir contexto |
| L14 | origem/natureza dos nomes de demonstração não está formalmente documentada | Média | confirmar uso exclusivo de dados fictícios |
| L15 | suíte de avaliação ainda não funciona como gate automatizado contínuo | Média | implementar CI |
| L16 | memória projetada ainda não foi incorporada ao procedimento de eliminação | Média | atualizar inventário ao implementar memória |
| L17 | workflow real de revisão humana não existe | Alta | criar estado de aprovação |
| L18 | identidade do revisor não é registrada | Alta | registrar usuário/revisor |
| L19 | não existe idempotência para `registrar_triagem` | Média | implementar chave de idempotência |
| L20 | não é possível comprovar todos os dados enviados ao provedor em uma execução histórica | Alta | registrar inventário mínimo de contexto |
| L21 | eliminação não cobre automaticamente todas as futuras estruturas | Alta | criar serviço centralizado de localização e eliminação |
| L22 | política vigente não é preservada como snapshot por decisão | Alta | registrar versão/hash das regras |

Nenhuma dessas lacunas deve ser interpretada como funcionalidade já existente.

A marcação explícita é parte da governança do protótipo.

---

# 17. Resposta à questão final

## Um auditor externo consegue verificar o sistema somente com o model card e o repositório?

**Parcialmente.**

Com este model card e o repositório, um auditor que nunca conversou com o grupo
consegue verificar vários aspectos concretos da autoridade do agente.

É possível observar que:

- o agente foi projetado para triagem;
- possui somente quatro ferramentas;
- não possui ferramenta para redefinir senhas ou alterar infraestrutura;
- pode consultar equipamentos, incidentes e regras;
- pode gravar triagens;
- possui limites técnicos de passos, tokens e tempo;
- existe uma execução registrada que pode ser parcialmente reconstruída;
- existe um procedimento documentado de revisão;
- foi executado um teste de eliminação com comparação antes e depois.

Também é possível verificar a evidência de eliminação em:

`evidencias/aula-12/saida-eliminacao.txt`

Entretanto, o auditor **ainda não consegue reconstruir integralmente qualquer
decisão histórica nem concluir que todos os controles estão garantidos fora do
modelo**.

Faltam, entre outros:

- versão imutável do modelo por execução;
- versão/hash do prompt;
- registro completo do destino dos dados;
- política de retenção;
- base legal de produção;
- gate determinístico de aprovação humana;
- identidade do revisor;
- informações de privilégios da credencial;
- mecanismo formal de suspensão.

Portanto, a resposta final é:

> O repositório atual permite uma auditoria parcial e fornece evidências reais
> sobre ferramentas, execução, revisão e eliminação. Porém, ainda existem
> lacunas de rastreabilidade e de aplicação de controles que impedem afirmar
> que todas as decisões podem ser completamente reconstruídas e governadas
> apenas com os registros atuais.

Essas limitações estão declaradas neste documento para que não sejam
confundidas com garantias já implementadas.
