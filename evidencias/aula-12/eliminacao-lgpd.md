# Evidência — Eliminação de dados pessoais

## 1. Objetivo

Este documento registra a execução de um pedido de eliminação de dados pessoais
no protótipo do Agente de Triagem de Suporte de TI.

O objetivo foi verificar, de forma executável, se os dados associados a um
titular de teste podem ser localizados, eliminados e posteriormente verificados
por uma consulta independente.

A saída integral da execução está registrada em:

`evidencias/aula-12/saida-eliminacao.txt`

O código utilizado no procedimento está em:

`scripts/teste_eliminacao_lgpd.py`

---

## 2. Titular utilizado

O teste utilizou exclusivamente dados fictícios criados para esta avaliação.

Identificador do titular:

`TITULAR_TESTE_LGPD_001`

Patrimônio associado:

`NB-LGPD-001`

Nenhuma pessoa real foi utilizada no procedimento.

---

## 3. Estruturas avaliadas

A análise do banco atual mostrou duas estruturas capazes de armazenar os dados
utilizados no teste.

### Tabela `equipamentos`

A tabela pode armazenar:

- patrimônio;
- nome ou identificador do usuário;
- tipo do equipamento;
- status;
- localização.

A estrutura está definida em:

`dados/init_db.py`

### Tabela `triagens`

A tabela pode armazenar:

- relato;
- categoria;
- prioridade;
- encaminhamento;
- justificativa;
- indicação de necessidade de humano.

A estrutura está definida em:

`dados/init_db.py`

e utilizada por:

`src/database.py`

---

# 4. Preparação do teste

Para evitar alteração dos dados utilizados pelo protótipo, o banco original:

`dados/suporte.db`

não foi modificado.

O procedimento criou uma cópia temporária do banco por meio do código:

`scripts/teste_eliminacao_lgpd.py`

Todos os dados fictícios foram inseridos apenas nessa cópia.

Isso permite executar a avaliação de eliminação sem comprometer a base usada
pelo restante do projeto.

---

# 5. Estado antes da eliminação

Antes da solicitação de eliminação, o titular fictício estava presente em duas
estruturas.

Resultado:

```text
Quantidade encontrada em equipamentos: 1
Quantidade encontrada em triagens: 1
