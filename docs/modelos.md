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

Para comparar os modelos de forma prática, serão utilizados os mesmos cinco casos de teste, com o mesmo prompt e os mesmos critérios de avaliação.

O objetivo não é produzir uma medição estatística, mas observar como cada modelo se comporta no domínio específico de triagem de chamados de suporte de TI.

### Prompt utilizado nos testes

O mesmo prompt será utilizado nos três modelos:

> Você é um agente responsável pela triagem inicial de chamados de suporte de TI.
>
> Analise o relato apresentado e produza uma resposta estruturada contendo:
>
> - categoria;
> - prioridade;
> - encaminhamento;
> - justificativa;
> - necessidade de intervenção humana.
>
> Não invente informações.
>
> Caso não existam informações suficientes para concluir a triagem com segurança, indique quais informações ainda precisam ser obtidas.
>
> Se houver divergência entre o relato do usuário e dados provenientes do sistema, considere os dados do sistema como evidência e explique a divergência.

### Casos utilizados

#### Caso 1 — Simples

Relato:

> "Não consigo entrar no meu e-mail corporativo. Quando coloco minha senha, aparece que ela está incorreta."

Resultado esperado:

- categoria: Acesso / Conta;
- prioridade: Média;
- encaminhamento: Suporte N1;
- intervenção humana: não obrigatória.

#### Caso 2 — Divergência

Relato:

> "Minha internet caiu novamente. Acho que meu notebook está com problema."

Informação encontrada no sistema:

> Existe um incidente ativo de indisponibilidade de rede no andar do usuário, afetando aproximadamente 35 funcionários.

Resultado esperado:

- categoria: Rede / Conectividade;
- reconhecer incidente geral;
- não tratar o notebook como causa confirmada;
- encaminhamento relacionado ao incidente de rede.

#### Caso 3 — Registro inexistente

Relato:

> "Meu notebook patrimônio NB-98451 parou de carregar."

Informação encontrada no sistema:

> O patrimônio NB-98451 não existe na base de equipamentos.

Resultado esperado:

- não inventar informações sobre o equipamento;
- informar que o registro não foi encontrado;
- solicitar confirmação do patrimônio ou outro identificador;
- não concluir a triagem como se o equipamento fosse válido.

#### Caso 4 — Não deve disparar a ação principal

Relato:

> "Vou trabalhar de casa amanhã. Como faço para configurar a VPN no notebook corporativo?"

Resultado esperado:

- reconhecer que se trata de solicitação informativa;
- não registrar automaticamente um incidente;
- fornecer ou buscar orientação sobre configuração de VPN.

#### Caso 5 — Ambíguo

Relato:

> "O sistema não está funcionando e preciso resolver isso urgente porque tenho coisa para entregar hoje."

Resultado esperado:

- não classificar definitivamente sem informações adicionais;
- perguntar qual sistema está sendo afetado;
- descobrir quem mais foi afetado;
- verificar mensagem de erro;
- avaliar impacto e urgência antes da classificação.

### Critérios de comparação

Para cada caso serão observados:

1. se o modelo identificou corretamente a categoria quando havia informação suficiente;
2. se respeitou a prioridade esperada;
3. se escolheu encaminhamento adequado;
4. se evitou inventar informações;
5. se reconheceu quando não havia informações suficientes;
6. se tratou corretamente divergências entre usuário e sistema;
7. se produziu resposta no formato solicitado.

### Registro dos resultados

A tabela abaixo será preenchida após a execução dos cinco casos nos três modelos.

| Caso | Mistral Small 4 | GPT-5.6 Luna | Gemini 3.8 Flash |
|---|---|---|---|
| 1 — Simples | A testar | A testar | A testar |
| 2 — Divergência | A testar | A testar | A testar |
| 3 — Registro inexistente | A testar | A testar | A testar |
| 4 — Não deve registrar incidente | A testar | A testar | A testar |
| 5 — Ambíguo | A testar | A testar | A testar |

Os testes serão executados utilizando o mesmo prompt e os mesmos dados para evitar favorecer qualquer um dos modelos.

Após a execução, será registrado para cada modelo se o resultado foi considerado adequado, parcialmente adequado ou inadequado, acompanhado de uma justificativa curta.

## 3.4 A decisão

A escolha inicial para a primeira implementação do agente será o **Mistral Small 4**.

A decisão foi tomada principalmente pelo equilíbrio entre:

- baixo custo estimado por execução;
- suporte a tool calling;
- suporte a saída estruturada;
- capacidade suficiente para interpretar chamados curtos de suporte;
- compatibilidade com a biblioteca `openai` por meio de `base_url`;
- proximidade com a infraestrutura utilizada nos laboratórios da disciplina.

Para a primeira versão do projeto, uma janela de contexto extremamente grande não é um requisito decisivo, pois o agente trabalhará com conversas relativamente curtas, poucas ferramentas e dados estruturados. Por isso, o custo e a capacidade de integração têm maior peso nesta etapa.

Essa escolha, entretanto, ainda será validada pela verificação prática dos cinco casos descritos na seção anterior.

### Condições para mudar de modelo

O grupo poderá mudar a escolha caso os testes demonstrem que outro candidato apresenta uma vantagem relevante.

A escolha será reconsiderada se ocorrer alguma das situações abaixo:

- o Mistral Small 4 não utilizar corretamente as ferramentas em pelo menos 4 dos 5 casos testados;
- o modelo produzir informações inexistentes ou ignorar retornos de erro das ferramentas;
- houver dificuldade recorrente em respeitar o formato estruturado solicitado;
- outro modelo apresentar resultados claramente melhores nos casos de divergência, registro inexistente e relato ambíguo;
- a diferença de qualidade justificar o aumento de custo;
- forem identificadas limitações técnicas durante a implementação do agente.

Portanto, a decisão atual é:

**Modelo inicialmente escolhido: Mistral Small 4.**

A escolha definitiva será confirmada depois da execução dos mesmos cinco casos nos três candidatos.

O objetivo não é selecionar o modelo mais poderoso de forma geral, mas o modelo com melhor equilíbrio entre qualidade, custo e requisitos específicos deste sistema.
