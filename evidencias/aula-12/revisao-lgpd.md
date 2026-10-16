# Evidência — Pedido de revisão de decisão automatizada

## 1. Objetivo

Este documento registra como seria atendido um pedido de revisão de decisão
automatizada relacionado ao Agente de Triagem de Suporte de TI.

A decisão utilizada é a mesma reconstruída em:

`evidencias/aula-12/decisao-reconstruida.md`

A evidência original da execução está em:

`logs/caso-divergencia.txt`

O objetivo é produzir uma explicação compreensível da decisão tomada pelo
agente, indicando os critérios e procedimentos utilizados, sem expor
informações desnecessárias ou segredos de negócio.

---

## 2. Decisão objeto da revisão

Na execução analisada, o agente produziu:

- **Categoria:** Rede / Conectividade
- **Prioridade:** Alta
- **Encaminhamento:** Suporte N2 (Equipe de Rede)
- **Necessidade de humano:** false

A justificativa registrada foi:

> Existe um incidente ativo de indisponibilidade de rede no Andar 3,
> afetando 35 usuários, o que indica um problema coletivo e não
> individualmente relacionado ao notebook do usuário.

A execução utilizou a ferramenta:

`consultar_incidentes`

O resultado retornado pela ferramenta informou a existência de um incidente
ativo:

- título: `Indisponibilidade de rede no andar 3`;
- categoria: `Rede / Conectividade`;
- localização: `Andar 3`;
- usuários afetados: `35`;
- status: `Ativo`.

### Evidências

- `logs/caso-divergencia.txt`
- `src/tools.py`
- `src/database.py`

---

# 3. Explicação que seria entregue ao titular

## Explicação da decisão

O chamado foi classificado pelo sistema como um problema de
**Rede / Conectividade**, com prioridade **Alta** e encaminhamento para
**Suporte N2 (Equipe de Rede)**.

Durante a análise, o agente consultou os incidentes ativos registrados no
sistema.

Essa consulta encontrou um incidente de indisponibilidade de rede localizado
no Andar 3, registrado como ativo e afetando 35 usuários.

A existência desse incidente coletivo foi utilizada como evidência para a
classificação do chamado como um problema de conectividade com impacto maior
que uma falha individual.

A prioridade Alta foi utilizada considerando o impacto coletivo identificado
na informação recuperada.

O encaminhamento para a equipe de rede decorreu da categoria atribuída ao
incidente e da natureza da indisponibilidade encontrada.

---

## Critérios utilizados

Os principais critérios utilizados na decisão foram:

1. existência de incidente ativo relacionado a rede;
2. quantidade de usuários afetados;
3. categoria do incidente encontrado;
4. status ativo do incidente;
5. regras de triagem disponíveis ao agente.

O sistema também possui uma regra de projeto segundo a qual incidentes gerais
não devem ser associados automaticamente a um usuário sem evidência de
correspondência.

Essa regra está especificada em:

`prompts/triagem-v1.txt`

---

## Procedimento utilizado

De forma simplificada, o procedimento observado foi:

```text
relato do usuário
        ↓
agente de triagem
        ↓
consulta de incidentes ativos
        ↓
incidente de rede encontrado
        ↓
classificação
        ↓
prioridade
        ↓
encaminhamento
