# Case — Agente Inteligente para Triagem Inicial de Chamados de Suporte de TI

## 1. O case — indústria e problema

### Setor

O case está inserido na área de Tecnologia da Informação, especificamente no processo interno de Service Desk e suporte de TI das organizações.

### Problema em uma frase

Analistas de suporte gastam tempo interpretando chamados incompletos, coletando informações adicionais e classificando manualmente a categoria, a prioridade e o encaminhamento correto de cada solicitação.

### Contexto do problema

Em um processo tradicional de suporte de TI, o usuário abre um chamado descrevendo o problema com suas próprias palavras. Como o solicitante normalmente não possui conhecimento técnico, é comum que a descrição inicial não contenha todas as informações necessárias para que o atendimento seja iniciado.

Relatos como "minha internet não funciona", "não consigo entrar no sistema" ou "meu computador está travando" podem ter diversas causas e níveis de impacto. Antes de encaminhar o chamado, o analista precisa interpretar o relato, identificar quais informações estão faltando, entrar em contato com o usuário quando necessário e consultar registros internos, como equipamentos cadastrados e incidentes conhecidos.

A triagem também precisa respeitar regras do domínio, como impacto do problema, urgência, quantidade de usuários afetados, existência de incidentes gerais e necessidade de escalonamento para equipes especializadas. Um problema que afeta apenas um usuário, por exemplo, pode exigir tratamento diferente de uma indisponibilidade que afeta todo um departamento.

Entre os casos que dificultam o processo estão:

- chamados com descrições vagas ou incompletas;
- usuários que atribuem uma causa incorreta ao problema;
- equipamentos ou identificadores informados que não existem no cadastro;
- existência de um incidente geral que explica um problema relatado como individual;
- solicitações classificadas pelo usuário como urgentes sem atender aos critérios de urgência;
- situações críticas que precisam obrigatoriamente de intervenção humana;
- chamados semelhantes que exigem encaminhamentos diferentes devido ao contexto.

Essas situações são importantes para o projeto porque exigem que o sistema interprete o contexto e descubra informações que não necessariamente foram fornecidas na primeira mensagem.

### O que a indústria já faz com agentes nesse problema

#### Broadcom

A Broadcom utiliza uma solução de IA da Moveworks para automatizar parte do suporte interno aos funcionários. Segundo o case publicado pela empresa fornecedora, a solução ultrapassou 75 mil questões de TI resolvidas e atingiu 88% de resolução autônoma das solicitações de suporte em 2025.

Pelo funcionamento descrito, o padrão de arquitetura aparenta combinar um agente conversacional com recuperação de conhecimento corporativo e integração com sistemas internos. O sistema interpreta a solicitação do funcionário e utiliza informações e ferramentas externas para tentar solucionar ou encaminhar o problema.

Apesar dos resultados divulgados, o material comercial não apresenta todos os detalhes necessários para avaliar o indicador isoladamente. Não fica completamente claro, por exemplo, quais tipos de solicitações fazem parte do denominador utilizado para calcular os 88%, qual o custo por atendimento ou como os casos incorretamente resolvidos são contabilizados.

#### Albemarle

A Albemarle adotou uma solução de IA para suporte aos funcionários em escala global. No case divulgado pela Moveworks, a empresa informa uma redução de 49% no tempo de resolução e que 80% dos tickets são resolvidos sem necessidade de trocas adicionais com a equipe de TI.

A arquitetura aparenta combinar um agente conversacional, acesso a uma base de conhecimento e integração com sistemas corporativos de suporte. A interpretação da solicitação ocorre em linguagem natural, enquanto informações externas são recuperadas para apoiar a resposta ou execução da tarefa.

Entretanto, a divulgação não apresenta em detalhes a distribuição dos tipos e da complexidade dos chamados analisados, o custo operacional da solução ou todos os critérios utilizados para considerar um ticket resolvido.

#### Unity

A Unity também utiliza uma solução de IA conversacional para suporte interno. Segundo o case divulgado pela Moveworks, determinados atendimentos passaram de aproximadamente três dias para menos de um minuto. O material também informa que 30% dos problemas de TI passaram a ser resolvidos sem intervenção humana.

O padrão de arquitetura aparenta envolver um agente conversacional integrado a bases de conhecimento e sistemas corporativos, permitindo que algumas solicitações sejam resolvidas automaticamente e outras sejam direcionadas para atendimento humano.

Apesar do resultado divulgado, não é informado detalhadamente se os três dias representam média, mediana ou um subconjunto específico de chamados. Também não são apresentados todos os custos e taxas de erro da automação, o que limita uma comparação direta com outros ambientes de suporte.

---

## 2. Os usuários, e como será a interação

### Perfis

| Perfil | O que ele quer | O que ele sabe | O que ele pode fazer |
|---|---|---|---|
| Solicitante | Resolver seu problema rapidamente e sem precisar conhecer termos técnicos | Conhece o problema que está enfrentando, mas não necessariamente sua causa | Descrever o problema, responder às perguntas e confirmar informações |
| Analista de suporte | Receber chamados com informações suficientes e corretamente classificados | Conhece o processo, as regras e os procedimentos técnicos | Revisar, corrigir e aprovar a triagem, além de assumir casos escalados |
| Gestor de suporte | Acompanhar a qualidade e o desempenho do processo | Conhece os indicadores e as regras gerais do atendimento | Consultar resultados e acompanhar indicadores |

### Usuário principal

O usuário principal será o solicitante.

O sistema será pensado para permitir que essa pessoa relate o problema utilizando linguagem natural, sem precisar conhecer previamente categorias técnicas, níveis de suporte ou qual equipe deve receber sua solicitação.

O analista de suporte continuará tendo autoridade para revisar as decisões do sistema e assumir situações nas quais o agente não possua informações suficientes ou identifique um caso que exija intervenção humana.

### Como será a interação

Inicialmente, a interação ocorrerá por meio de chat ou terminal.

A conversa será iniciada pelo solicitante, que descreve livremente o problema. A partir dessa primeira mensagem, o agente identifica quais informações já estão disponíveis e quais ainda precisam ser descobertas.

Em vez de apresentar sempre o mesmo formulário, o agente poderá fazer perguntas diferentes de acordo com o contexto. São esperadas, em média, entre duas e cinco trocas para que o sistema obtenha informações suficientes para realizar a triagem.

Quando conseguir concluir a análise, o sistema devolverá uma resposta estruturada contendo:

- categoria;
- prioridade;
- encaminhamento sugerido;
- resumo do problema;
- justificativa da classificação.

Quando não houver informações suficientes, existir uma divergência relevante ou o caso exigir intervenção humana, o sistema deverá informar que não conseguiu concluir a triagem com segurança e encaminhar o contexto coletado para um analista.

### Exemplo de diálogo

**Usuário:**  
Meu computador não conecta na internet e preciso fazer uma apresentação daqui a pouco.

**Agente:**  
O problema acontece somente no seu computador ou outras pessoas próximas também estão sem conexão?

**Usuário:**  
Pelo que vi, só no meu.

**Agente:**  
Você está utilizando Wi-Fi ou cabo? O computador apresenta alguma mensagem de erro?

**Usuário:**  
Wi-Fi. Ele aparece conectado, mas sem internet.

**Agente:**  
Não encontrei um incidente geral de rede registrado neste momento. Com as informações disponíveis, a triagem sugerida é:

**Categoria:** Rede / Conectividade  
**Prioridade:** Alta  
**Encaminhamento:** Suporte N1  
**Resumo:** Equipamento conectado ao Wi-Fi, porém sem acesso à internet, sem evidência de indisponibilidade geral.

O chamado pode seguir para o atendimento do Suporte N1 com as informações coletadas.

### O que o usuário não informa de primeira?

Dependendo do problema, o agente poderá precisar descobrir informações como:

- qual equipamento está sendo utilizado;
- qual sistema ou serviço foi afetado;
- qual mensagem de erro apareceu;
- quando o problema começou;
- se outras pessoas também foram afetadas;
- quais tentativas de solução já foram realizadas;
- qual é o impacto da indisponibilidade;
- se existe alguma atividade crítica relacionada ao problema.

A necessidade dessas informações varia conforme cada relato. Essa característica faz com que a interação não possa ser reduzida simplesmente ao preenchimento de um conjunto fixo de perguntas.

---

## 3. Os ganhos esperados

### Por que um agente, e não software comum?

A tarefa exige interpretar relatos abertos e incompletos e decidir, durante a própria execução, quais informações adicionais precisam ser solicitadas ou consultadas antes que uma classificação possa ser realizada.

Um formulário tradicional poderia coletar campos previamente definidos, mas faria perguntas fixas independentemente do problema apresentado. O agente pode adaptar a investigação conforme o relato do usuário, suas respostas e as informações encontradas durante o processo.

### Eixos de ganho

O principal eixo escolhido será o **tempo por tarefa**, especificamente o tempo necessário para realizar a triagem inicial de um chamado.

Para este case, foi estabelecida uma linha de base de **2 minutos e 7 segundos por triagem**, considerando dez situações diferentes de suporte de TI.

Os casos utilizados cobrem situações simples, ambíguas e de divergência, de forma a representar diferentes dificuldades encontradas durante a triagem.

| Caso | Situação | Tempo |
|---|---|---:|
| 1 | Problema de acesso ao e-mail | 1min45s |
| 2 | Notebook sem acesso à internet | 2min05s |
| 3 | Sistema corporativo indisponível | 1min50s |
| 4 | Computador lento | 2min35s |
| 5 | Suspeita de phishing | 1min55s |
| 6 | Equipamento não encontrado no cadastro | 2min25s |
| 7 | Problema de impressão | 2min10s |
| 8 | Divergência com incidente geral de rede | 2min20s |
| 9 | Solicitação de configuração de VPN | 1min30s |
| 10 | Relato insuficiente e ambíguo | 2min40s |
| **Média** | **10 casos** | **2min07s por triagem** |

A linha de base adotada para comparação será, portanto:

**Tempo médio de triagem: 2min07s por chamado.**

### Alvo

O objetivo será avaliar se o agente consegue reduzir o tempo médio de triagem de **2min07s para até 1min00s por chamado**.

Caso esse resultado seja alcançado, a redução será de aproximadamente **53% no tempo por triagem**.

Esse percentual representa o **alvo do projeto**. O ganho efetivamente obtido será calculado posteriormente, após a implementação e os testes do agente.

| Eixo | Linha de base | Alvo | Ganho esperado | Volume |
|---|---:|---:|---:|---:|
| Tempo por triagem | 2min07s por chamado | até 1min00s por chamado | aproximadamente 53% de redução | 10 casos |

O ganho será calculado utilizando:

**Ganho (%) = (tempo médio manual - tempo médio com agente) / tempo médio manual × 100**

Aplicando o alvo:

**Ganho (%) = (127 - 60) / 127 × 100**

**Ganho esperado ≈ 52,76%**

Arredondando, o objetivo é obter aproximadamente **53% de redução no tempo médio de triagem**.

### Ganho para o negócio

Para a área de suporte, o ganho esperado é reduzir o tempo operacional utilizado na triagem inicial dos chamados e permitir que os analistas concentrem maior parte de seu trabalho no diagnóstico e na resolução dos problemas.

Outro benefício esperado é aumentar a padronização das informações recebidas pelo suporte, reduzindo a necessidade de iniciar o atendimento buscando dados básicos que poderiam ter sido coletados anteriormente.

### Ganho para o usuário

Para o solicitante, o principal ganho esperado é poder descrever seu problema naturalmente, sem precisar conhecer categorias técnicas ou descobrir sozinho qual equipe deve atendê-lo.

O agente deverá solicitar somente as informações relevantes para o contexto apresentado, reduzindo perguntas desnecessárias e repetições.

Existe, entretanto, uma possível tensão entre o ganho do negócio e o ganho do usuário. Tentar automatizar uma quantidade excessiva de chamados poderia reduzir a carga operacional dos analistas, mas prejudicar a experiência em situações complexas.

Por esse motivo, casos ambíguos, críticos ou sem informações suficientes continuarão sendo encaminhados para atendimento humano.
