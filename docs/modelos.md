# Análise de Modelos

## 3.1 Os candidatos

Para este projeto, foram escolhidos três modelos candidatos de provedores diferentes:

- **Mistral Small 4**
- **GPT-5.6 Luna**
- **Gemini 3.8 Flash**

A comparação foi feita considerando os critérios que mais importam para o case de triagem de chamados de suporte de TI.

O sistema precisa interpretar linguagem natural, produzir respostas estruturadas, utilizar ferramentas externas, manter baixa latência e ter custo suficientemente baixo para permitir várias chamadas por atendimento.

Multimídia não é um requisito importante nesta primeira versão, pois a entrada será predominantemente textual.

### Critérios escolhidos

- **Tool calling:** necessário porque o agente deverá consultar equipamentos, incidentes e registrar triagens.
- **Saída estruturada:** necessária para produzir categoria, prioridade, encaminhamento e justificativa em formato previsível.
- **Capacidade de raciocínio:** importante para lidar com relatos incompletos, ambiguidades e divergências entre o usuário e os registros consultados.
- **Janela de contexto:** útil para carregar o histórico do atendimento, regras e resultados das ferramentas.
- **Latência:** o usuário estará aguardando a resposta durante uma conversa interativa.
- **Custo:** cada atendimento poderá utilizar várias chamadas ao modelo.
- **Compatibilidade com a biblioteca OpenAI:** importante porque a disciplina exige o uso da biblioteca `openai`.
- **Política de dados:** relevante porque o domínio de suporte pode envolver informações corporativas, mesmo que neste projeto os dados sejam simulados.

### Comparação inicial

| Critério | Mistral Small 4 | GPT-5.6 Luna | Gemini 3.8 Flash |
|---|---|---|---|
| Provedor | Mistral AI | OpenAI | Google |
| ID do modelo | `mistral-small-2603` | `gpt-5.6-luna` | `gemini-3.8-flash` |
| Janela de contexto | 256 mil tokens | 1,05 milhão de tokens | 1 milhão de tokens |
| Tool / Function Calling | Sim | Sim | Sim |
| Saída estruturada | Sim | Sim | Sim |
| Raciocínio | Sim | Sim | Sim |
| Multimídia | Disponível, mas não necessária para este case | Disponível, mas não necessária para este case | Disponível, mas não necessária para este case |
| Compatível com biblioteca `openai` | Sim, por `base_url` compatível | Sim, nativamente | Sim, por endpoint compatível com OpenAI |
| Preço de entrada | US$ 0,15 / 1 milhão de tokens | US$ 0,20 / 1 milhão de tokens | US$ 0,75 / 1 milhão de tokens |
| Preço de saída | US$ 0,60 / 1 milhão de tokens | US$ 1,20 / 1 milhão de tokens | US$ 3,75 / 1 milhão de tokens |
| Perfil esperado no projeto | Baixo custo e bom suporte a ferramentas | Bom equilíbrio entre custo e capacidade | Maior custo, com forte capacidade agêntica |

### Observações sobre os candidatos

#### Mistral Small 4

O Mistral Small 4 é um modelo de baixo custo com suporte nativo a function calling e saídas estruturadas.

Sua janela de contexto de 256 mil tokens é mais do que suficiente para a primeira versão do projeto, que trabalhará com conversas curtas, dados estruturados e poucas ferramentas.

Por possuir custo baixo, é um candidato interessante para um agente que poderá realizar múltiplas chamadas durante um único atendimento.

#### GPT-5.6 Luna

O GPT-5.6 Luna é voltado para cargas de trabalho sensíveis a custo e possui uma janela de contexto de aproximadamente 1,05 milhão de tokens.

O modelo oferece suporte a funções e pode ser utilizado diretamente por meio da biblioteca `openai`, simplificando a implementação exigida pela disciplina.

Seu custo é maior do que o Mistral Small 4, porém ainda permanece baixo para o volume previsto neste protótipo.

#### Gemini 3.8 Flash

O Gemini 3.8 Flash é um modelo voltado para fluxos agênticos e tarefas de múltiplas etapas.

Possui janela de contexto de 1 milhão de tokens, suporte a function calling e pode ser acessado utilizando a própria biblioteca `openai` por meio do endpoint de compatibilidade fornecido pelo Google.

Entre os três candidatos, apresenta custo de tokens superior para este caso, mas será mantido na comparação para verificar se a qualidade das respostas compensa essa diferença.

## 3.2 A conta de custo

Para estimar o custo do agente, foi considerado um atendimento médio com aproximadamente **4 chamadas ao modelo**.

A estimativa por chamada é:

- 800 tokens de entrada;
- 250 tokens de saída.

Portanto, uma execução completa utiliza aproximadamente:

- **3.200 tokens de entrada**;
- **1.000 tokens de saída**.

Esses valores são estimativas iniciais. O consumo real será medido quando o agente estiver implementado.

### Fórmula utilizada

Custo de entrada:

`tokens de entrada / 1.000.000 × preço por milhão`

Custo de saída:

`tokens de saída / 1.000.000 × preço por milhão`

Custo total:

`custo de entrada + custo de saída`

### Mistral Small 4

Preço considerado:

- Entrada: US$ 0,15 por 1 milhão de tokens
- Saída: US$ 0,60 por 1 milhão de tokens

Cálculo:

`3.200 / 1.000.000 × 0,15 = US$ 0,00048`

`1.000 / 1.000.000 × 0,60 = US$ 0,00060`

**Custo estimado por execução: US$ 0,00108**

Para 100 execuções:

`0,00108 × 100 = US$ 0,108`

Para uma estimativa de 1.000 execuções durante o semestre:

`0,00108 × 1.000 = US$ 1,08`

### GPT-5.6 Luna

Preço considerado:

- Entrada: US$ 0,20 por 1 milhão de tokens
- Saída: US$ 1,20 por 1 milhão de tokens

Cálculo:

`3.200 / 1.000.000 × 0,20 = US$ 0,00064`

`1.000 / 1.000.000 × 1,20 = US$ 0,00120`

**Custo estimado por execução: US$ 0,00184**

Para 100 execuções:

`0,00184 × 100 = US$ 0,184`

Para uma estimativa de 1.000 execuções durante o semestre:

`0,00184 × 1.000 = US$ 1,84`

### Gemini 3.8 Flash

Preço considerado:

- Entrada: US$ 0,75 por 1 milhão de tokens
- Saída: US$ 3,75 por 1 milhão de tokens

Cálculo:

`3.200 / 1.000.000 × 0,75 = US$ 0,00240`

`1.000 / 1.000.000 × 3,75 = US$ 0,00375`

**Custo estimado por execução: US$ 0,00615**

Para 100 execuções:

`0,00615 × 100 = US$ 0,615`

Para uma estimativa de 1.000 execuções durante o semestre:

`0,00615 × 1.000 = US$ 6,15`

### Comparação

| Modelo | 1 execução | 100 execuções | 1.000 execuções |
|---|---:|---:|---:|
| Mistral Small 4 | US$ 0,00108 | US$ 0,108 | US$ 1,08 |
| GPT-5.6 Luna | US$ 0,00184 | US$ 0,184 | US$ 1,84 |
| Gemini 3.8 Flash | US$ 0,00615 | US$ 0,615 | US$ 6,15 |

Considerando apenas o custo estimado, o **Mistral Small 4** é o candidato mais barato entre os três.

Entretanto, o custo não será utilizado isoladamente para escolher o modelo. A decisão também levará em consideração a qualidade das respostas nos cinco casos de teste, capacidade de uso de ferramentas, saída estruturada e comportamento diante de situações ambíguas.

A estimativa de 1.000 execuções representa apenas uma referência de volume para o semestre. O custo real dependerá da quantidade de chamadas realizadas, do tamanho das mensagens e do número de testes executados durante o desenvolvimento.

## 3.3 A verificação mínima

A verificação foi planejada inicialmente para utilizar cinco casos de teste e três modelos candidatos, mantendo o mesmo prompt, os mesmos dados e os mesmos critérios de avaliação.

O objetivo dessa comparação não era produzir uma medição estatística, mas observar o comportamento dos modelos no domínio específico de triagem de chamados de suporte de TI.

Durante a implementação do protótipo, entretanto, a verificação prática foi concentrada no modelo efetivamente utilizado pelo agente, devido ao escopo da entrega, à disponibilidade das APIs e às limitações encontradas durante os testes.

Os demais modelos permanecem registrados como candidatos da análise inicial, mas não são apresentados como modelos executados nesta versão do protótipo.

### Prompt utilizado nos testes

O agente utiliza o prompt armazenado em:

`prompts/triagem-v1.txt`

O prompt define o agente como responsável exclusivamente pela triagem inicial de chamados de suporte de TI e estabelece regras para:

- interpretar o relato do usuário;
- identificar categoria e prioridade;
- utilizar ferramentas apenas quando necessário;
- evitar invenção de informações;
- diferenciar problemas individuais de incidentes coletivos;
- tratar registros inexistentes;
- reconhecer solicitações informativas;
- encaminhar casos críticos, contraditórios ou inseguros para atendimento humano;
- produzir uma saída final estruturada.

O prompt também utiliza exemplos de comportamento esperado para reduzir associações incorretas entre o relato do usuário e informações encontradas nas ferramentas.

### Casos definidos para avaliação

#### Caso 1 — Simples

Relato:

> "Não consigo entrar no meu e-mail corporativo. Quando coloco minha senha, aparece que ela está incorreta."

Resultado esperado:

- categoria: Acesso / Conta;
- prioridade: Média;
- encaminhamento: Suporte N1;
- intervenção humana: não obrigatória;
- não consultar incidentes gerais sem evidência de impacto coletivo.

#### Caso 2 — Divergência

Relato:

> "Estou no Andar 3 e minha internet caiu. Acho que meu notebook está com problema."

Informação encontrada no sistema:

> Existe um incidente ativo de indisponibilidade de rede no Andar 3, afetando aproximadamente 35 usuários.

Resultado esperado:

- categoria: Rede / Conectividade;
- reconhecer o incidente geral;
- utilizar os dados do sistema como evidência;
- não tratar o notebook como causa confirmada;
- encaminhar o caso de acordo com o incidente de rede.

#### Caso 3 — Registro inexistente

Relato:

> "Meu notebook patrimônio NB-98451 parou de carregar."

Informação encontrada no sistema:

> O patrimônio NB-98451 não existe na base de equipamentos.

Resultado esperado:

- não inventar informações sobre o equipamento;
- reconhecer o retorno de registro inexistente;
- solicitar confirmação do patrimônio ou outro identificador quando necessário;
- não concluir a análise como se o equipamento fosse válido.

#### Caso 4 — Não deve registrar incidente

Relato:

> "Vou trabalhar de casa amanhã. Como faço para configurar a VPN no notebook corporativo?"

Resultado esperado:

- categoria: Solicitação Informativa;
- prioridade: Baixa;
- encaminhamento: Orientação ao usuário;
- não registrar automaticamente um incidente;
- não utilizar ferramentas de incidentes quando não houver falha relatada.

#### Caso 5 — Ambíguo

Relato:

> "O sistema não está funcionando e preciso resolver isso urgente porque tenho coisa para entregar hoje."

Resultado esperado:

- não classificar definitivamente sem informações adicionais;
- perguntar qual sistema está sendo afetado;
- descobrir se outras pessoas também foram afetadas;
- verificar mensagem de erro;
- avaliar impacto e urgência antes da classificação.

O caso ambíguo permanece definido para evolução e avaliações posteriores do agente, mas não foi incluído nos logs finais desta versão do protótipo.

### Critérios de avaliação

Para os casos executados foram observados:

1. se o agente identificou corretamente a categoria quando havia informação suficiente;
2. se respeitou a prioridade esperada;
3. se escolheu encaminhamento adequado;
4. se evitou inventar informações;
5. se reconheceu quando não havia informações suficientes;
6. se tratou corretamente divergências entre usuário e sistema;
7. se utilizou as ferramentas somente quando necessário;
8. se produziu resposta compatível com o formato solicitado.

### Registro dos resultados

A verificação prática desta versão foi realizada com o modelo `ministral-3b-2512`.

| Caso | Comportamento esperado | Resultado |
|---|---|---|
| 1 — Simples | Classificar senha incorreta como Acesso / Conta sem consultar incidentes gerais | Aprovado |
| 2 — Divergência | Consultar incidentes e priorizar a evidência de indisponibilidade coletiva | Aprovado |
| 3 — Registro inexistente | Não inventar dados para patrimônio inexistente | Aprovado |
| 4 — Não deve registrar incidente | Reconhecer solicitação informativa sem gerar incidente | Aprovado |
| 5 — Ambíguo | Coletar informações adicionais antes de concluir | Não executado nesta versão |

Os registros completos das quatro execuções realizadas estão armazenados na pasta `logs/`:

- `logs/caso-simples.txt`
- `logs/caso-divergencia.txt`
- `logs/caso-registro-inexistente.txt`
- `logs/caso-nao-dispara.txt`

Os modelos GPT-5.6 Luna e Gemini 3.8 Flash permaneceram como candidatos da análise inicial, porém não foram executados nesta versão do protótipo. Por esse motivo, não são apresentados resultados experimentais para esses modelos.

## 3.4 A decisão

### Decisão inicial

Na etapa de planejamento, o modelo inicialmente escolhido foi o **Mistral Small 4**, principalmente pelo equilíbrio esperado entre:

- baixo custo estimado;
- suporte a tool calling;
- suporte a saída estruturada;
- capacidade suficiente para interpretar chamados curtos de suporte;
- compatibilidade com a biblioteca `openai` por meio de `base_url`;
- adequação ao escopo acadêmico do protótipo.

A análise inicial também considerou GPT-5.6 Luna e Gemini 3.8 Flash como alternativas.

### Ajuste realizado durante a implementação

Durante a implementação prática, o projeto passou a utilizar o modelo:

`ministral-3b-2512`

A mudança ocorreu durante os testes de integração com a API da Mistral.

O modelo inicialmente configurado apresentou limitações de uso durante as chamadas realizadas no ambiente disponível. O `ministral-3b-2512` apresentou acesso funcional pela mesma API e foi suficiente para executar o fluxo necessário ao protótipo.

Essa alteração não exigiu uma mudança estrutural no agente, porque a implementação utiliza o SDK `openai` com endereço de API configurável por variável de ambiente.

A configuração utilizada ficou baseada nas variáveis:

- `OPENAI_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`

Dessa forma, o provedor ou modelo pode ser alterado sem reescrever toda a arquitetura do sistema.

### Modelo utilizado na versão entregue

Portanto, o modelo efetivamente utilizado na implementação e nos testes registrados desta versão foi:

**`ministral-3b-2512`**

Essa escolha prática foi suficiente para:

- interpretar os relatos utilizados nos testes;
- utilizar function calling;
- consultar ferramentas externas;
- considerar retornos do banco de dados;
- distinguir situações individuais de incidentes gerais;
- lidar com registro inexistente;
- reconhecer solicitações informativas;
- produzir a classificação de triagem.

### Possibilidade de evolução

A arquitetura permite que outros modelos sejam testados posteriormente.

Em uma evolução do trabalho, GPT-5.6 Luna, Gemini 3.8 Flash ou versões mais novas de modelos da Mistral poderão ser submetidos aos mesmos casos de teste.

A substituição poderá ser considerada caso outro modelo apresente vantagens relevantes em:

- uso correto das ferramentas;
- aderência ao contrato de saída;
- tratamento de ambiguidades;
- quantidade de informações inventadas;
- latência;
- custo;
- estabilidade da API.

O objetivo não é escolher o modelo mais poderoso de forma geral, mas utilizar um modelo adequado aos requisitos específicos do agente.

## 3.5 Resultados da verificação

Após a implementação do protótipo, o agente foi executado com quatro casos representativos do domínio.

Os resultados permitiram verificar tanto o comportamento esperado quanto problemas encontrados durante o desenvolvimento.

### Caso simples

Entrada:

> "Não consigo entrar no meu e-mail corporativo. Quando coloco minha senha, aparece que ela está incorreta."

Resultado final:

- categoria: Acesso / Conta;
- prioridade: Média;
- encaminhamento: Suporte N1;
- intervenção humana: não necessária;
- ferramentas utilizadas: nenhuma.

O agente concluiu corretamente que o relato apresentava informação suficiente para a triagem e não realizou consultas desnecessárias.

### Caso de divergência

Entrada:

> "Estou no Andar 3 e minha internet caiu. Acho que meu notebook está com problema."

O agente utilizou a ferramenta `consultar_incidentes`.

A consulta encontrou um incidente ativo de indisponibilidade de rede no Andar 3, afetando aproximadamente 35 usuários.

Nesse caso, o agente priorizou a evidência encontrada no sistema em relação à hipótese inicial do usuário de que o notebook seria a causa do problema.

O comportamento foi considerado adequado.

### Caso de registro inexistente

Entrada:

> "Meu notebook patrimônio NB-98451 parou de carregar."

O agente utilizou a consulta de equipamento e recebeu a informação de que o patrimônio não estava cadastrado.

O sistema tratou o retorno de registro inexistente como uma informação válida e não criou dados fictícios sobre o equipamento.

Esse comportamento foi considerado adequado.

### Caso que não deve disparar incidente

Entrada:

> "Vou trabalhar de casa amanhã. Como faço para configurar a VPN no notebook corporativo?"

O agente reconheceu que o relato representa uma solicitação informativa e não uma falha de TI.

O resultado esperado definido para esse tipo de situação é:

- categoria: Solicitação Informativa;
- prioridade: Baixa;
- encaminhamento: Orientação ao usuário;
- intervenção humana: não necessária.

Nenhuma ferramenta de consulta de incidentes foi necessária.

### Resumo dos resultados

| Caso | Resultado |
|---|---|
| Simples | Aprovado |
| Divergência | Aprovado |
| Registro inexistente | Aprovado |
| Não dispara | Aprovado |
| Ambíguo | Não executado nesta versão |

Os registros completos das execuções estão disponíveis na pasta `logs/`.

### Modelo utilizado no protótipo

Durante os testes foi utilizado o modelo:

`ministral-3b-2512`

O modelo foi acessado pela API da Mistral utilizando o SDK `openai` e uma `base_url` configurável.

Essa estratégia mantém a implementação desacoplada de um único endpoint e facilita a substituição do modelo em versões futuras.

### Orçamento do agente

O agente possui limites explícitos de execução:

- máximo de 5 passos;
- máximo de 5.000 tokens;
- máximo de 60 segundos por execução.

Esses limites foram implementados para impedir execução indefinida e controlar a autonomia do agente.

Caso algum limite seja atingido sem uma resposta segura, o sistema encerra o fluxo automático e pode encaminhar o caso para atendimento humano.

### Refinamentos realizados durante os testes

A primeira execução do caso simples revelou um problema importante.

Mesmo diante de um relato explícito de senha incorreta, o agente consultou os incidentes ativos e associou indevidamente o chamado a uma indisponibilidade de rede no Andar 3.

Não havia evidência no relato de que o usuário estivesse naquele local.

Isso demonstrou que apenas disponibilizar uma ferramenta ao modelo não é suficiente para garantir seu uso correto.

Para corrigir o comportamento foram realizados dois ajustes principais:

1. refinamento das descrições das ferramentas;
2. refinamento do system prompt.

A ferramenta de consulta de incidentes passou a informar explicitamente que deve ser utilizada somente quando houver indícios de:

- indisponibilidade geral;
- falha de rede;
- múltiplos usuários afetados;
- impacto coletivo;
- sistema ou serviço indisponível.

O prompt também passou a proibir a associação automática entre um incidente ativo e um chamado individual sem evidência concreta.

Além disso, foram acrescentadas regras específicas para:

- problemas individuais de senha e autenticação;
- solicitações informativas;
- registros inexistentes;
- uso de patrimônio;
- localização do usuário;
- encaminhamento para atendimento humano.

### Resultado após o refinamento

Após as alterações, o mesmo caso de senha foi executado novamente.

O agente retornou:

- categoria: Acesso / Conta;
- prioridade: Média;
- encaminhamento: Suporte N1;
- `precisa_humano`: false.

Nenhuma ferramenta foi utilizada nessa execução.

Esse resultado demonstrou uma melhora importante no comportamento do agente, pois ele passou a utilizar menor autonomia quando o próprio relato já continha informações suficientes para concluir a triagem.

### Conclusão da verificação

A implementação mostrou que o desempenho de um agente não depende apenas do modelo utilizado.

O comportamento final também depende de:

- clareza do system prompt;
- descrição das ferramentas;
- contratos de entrada e saída;
- dados disponíveis;
- regras do domínio;
- limites de autonomia;
- tratamento de erros;
- testes com casos representativos.

Os testes também mostraram que ferramentas não devem ser chamadas simplesmente porque estão disponíveis.

O agente deve decidir se a consulta realmente acrescenta informação necessária ao processo.

A versão final do protótipo conseguiu diferenciar:

- problemas individuais de acesso;
- incidentes coletivos;
- registros inexistentes;
- solicitações informativas.

Como evolução futura, o caso ambíguo poderá ser executado juntamente com testes comparativos usando outros modelos, permitindo ampliar a avaliação de qualidade, custo e comportamento do agente.
