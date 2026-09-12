# Arquitetura V1 — Agente Inteligente para Triagem Inicial de Chamados de Suporte de TI

## 1. Entrada

### O que chega ao sistema

A entrada principal do sistema será uma mensagem de texto livre escrita pelo solicitante descrevendo um problema relacionado ao suporte de TI.

Exemplos:

- "Meu computador está conectado no Wi-Fi, mas não entra na internet."
- "Não consigo acessar o sistema da empresa."
- "Meu notebook está muito lento."
- "Esqueci minha senha e não consigo entrar."
- "O sistema parou de funcionar para todo o setor."

O usuário não precisará selecionar previamente categoria, prioridade ou equipe responsável. Essas informações serão determinadas durante a triagem.

### De onde vem e quem dispara

O próprio solicitante inicia a interação por meio de um chat.

O sistema não inicia o atendimento sozinho. Ele é acionado quando o usuário envia a primeira mensagem descrevendo o problema.

### Heterogeneidade da entrada

Apesar de todas as entradas serem mensagens de texto relacionadas a suporte de TI, os problemas podem pertencer a diferentes contextos.

Para a primeira versão do projeto, considera-se aproximadamente:

- 35% — problemas de acesso, conta ou senha;
- 25% — problemas de conectividade;
- 20% — problemas de software ou sistemas;
- 15% — problemas de equipamento;
- 5% — incidentes gerais ou situações que precisam de análise humana.

Como todas as entradas são relatos de suporte da mesma natureza, não será utilizado um Router dedicado na entrada nesta primeira versão.

---

## 2. System

### System prompt

O agente é um assistente de triagem inicial de suporte de TI que coleta as informações necessárias, consulta dados disponíveis e sugere categoria, prioridade e encaminhamento do chamado, mas não realiza alterações críticas em equipamentos, contas ou sistemas.

### Ferramentas

| Ferramenta | Função | Tipo | Escrita | Reversível |
|---|---|---|---|---|
| consultar_equipamento | Consultar informações do equipamento informado pelo usuário | Leitura | Não | — |
| consultar_incidentes | Verificar incidentes gerais conhecidos | Leitura | Não | — |
| consultar_base_suporte | Consultar categorias, procedimentos e regras de triagem | Leitura | Não | — |
| registrar_triagem | Registrar o resultado da triagem do chamado | Escrita | Sim | Sim |
| encaminhar_humano | Encaminhar casos ambíguos ou críticos para análise humana | Escrita | Sim | Sim |

Nenhuma alteração crítica em contas, equipamentos ou sistemas será executada automaticamente pelo agente.

### Estado

Durante o atendimento, o sistema deverá manter:

- problema informado pelo usuário;
- informações já coletadas;
- perguntas já realizadas;
- respostas recebidas;
- equipamento ou serviço afetado;
- quantidade de usuários afetados;
- impacto informado;
- incidentes encontrados;
- tentativas de solução já realizadas;
- categoria sugerida;
- prioridade sugerida;
- encaminhamento sugerido;
- número de passos utilizados.

Essas informações evitam perguntas repetidas e permitem que cada etapa utilize apenas os dados necessários produzidos anteriormente.

### Orçamento

Para a primeira versão:

- `MAX_PASSOS_AGENTE = 5`
- `MAX_PERGUNTAS = 4`
- `MAX_TOKENS = 4000`
- `MAX_TEMPO = 60 segundos`

Caso o agente não consiga reunir informações suficientes dentro desses limites, o chamado deverá ser encaminhado para análise humana.

---

## 3. Processamento

### Esboço do fluxo

```text
1. ENTRADA
   Recebe mensagem de texto livre do solicitante
   [—]

        ↓

2. EXTRAÇÃO
   Identifica problema, equipamento, serviço,
   impacto e informações ausentes
   [LLM]

        ↓

3. COLETA
   Decide quais informações adicionais precisam
   ser perguntadas ao usuário
   [AGENTE — MAX_PASSOS = 5]

        ↓

4. CONSULTA
   Consulta equipamento, incidentes conhecidos
   e regras da base de suporte
   [FERRAMENTAS — LEITURA]

        ↓

5. CLASSIFICAÇÃO
   Determina categoria, prioridade e
   encaminhamento sugerido
   [LLM]

        ↓

6. REGISTRO
   Registra a triagem produzida
   [ESCRITA — REVERSÍVEL]

        ↓

7. RETORNO
   Apresenta ao usuário o resumo da triagem
   e informa o encaminhamento
   [—]
