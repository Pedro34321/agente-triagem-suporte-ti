# Memória do Agente de Triagem de Suporte de TI

## 1. Objetivo

O agente desenvolvido neste projeto realiza a triagem inicial de chamados de suporte de TI. Ele recebe o relato do usuário, interpreta o problema, consulta ferramentas quando necessário e produz uma classificação com categoria, prioridade e encaminhamento.

Na versão atual, cada execução começa praticamente do zero. Mesmo que o agente já tenha lidado com uma situação semelhante anteriormente, essa experiência não é automaticamente utilizada em uma nova execução.

Este documento define como a memória do agente deverá funcionar. A decisão é dividida em dois pontos principais:

1. como o agente lembra;
2. como o agente esquece.

O objetivo não é armazenar tudo o que passa pelo agente. A política adotada é guardar somente informações que possuam utilidade futura, origem confiável e necessidade real de persistência.

---

# Decisão 1 — Como o agente lembra

## 1.1 Os dois níveis de memória

O projeto utilizará dois níveis principais de memória: **curto prazo** e **longo prazo**.

| Característica | Curto prazo | Longo prazo |
|---|---|---|
| O que é | Estado da execução atual do chamado | Informações que atravessam diferentes execuções |
| Conteúdo no case | Relato atual, objetivo da triagem, trajetória do agente, ferramentas chamadas, resultados obtidos, classificação parcial e estado de operações já realizadas | Experiências anteriores relevantes, fatos atuais do domínio e regras de funcionamento do agente |
| Persistido como | Checkpoint estruturado, um por execução | Índice, tabela chave-valor e texto versionado |
| Como é lido | Carregado integralmente quando uma execução é retomada | Recuperado somente quando necessário |
| Forma de acesso | Pelo identificador da execução | Por similaridade, chave ou versão |
| Ciclo de vida | Existe enquanto a execução puder ser retomada | Pode permanecer entre várias execuções |
| Finalidade | Permitir que o agente continue de onde parou | Permitir que o agente utilize conhecimentos anteriores relevantes |

A diferença mais importante é que a memória de curto prazo pertence a uma execução específica, enquanto a memória de longo prazo pode ser utilizada por diferentes chamados.

---

### O que deve existir no checkpoint

Cada execução terá um identificador único, por exemplo:

`execution_id = triagem-2026-000123`

O checkpoint deverá guardar informações suficientes para que o agente consiga retomar a execução sem começar novamente do zero.

Exemplo da estrutura planejada:

```json
{
  "execution_id": "triagem-2026-000123",
  "criado_em": "timestamp",
  "atualizado_em": "timestamp",
  "modelo": "ministral-3b-2512",
  "versao_prompt": "triagem-v1",
  "objetivo": "realizar triagem inicial",
  "relato": "relato atual do usuário",
  "passo_atual": 2,
  "passos_executados": 2,
  "tokens_utilizados": 3100,
  "ferramentas_executadas": [],
  "resultados_ferramentas": [],
  "memorias_recuperadas": [],
  "classificacao_parcial": null,
  "perguntas_pendentes": [],
  "escritas_realizadas": [],
  "aguardando_aprovacao_humana": false,
  "motivo_termino": null
}
```

Além disso, cada chamada de ferramenta deverá possuir um registro mínimo.

Exemplo:

```json
{
  "ferramenta": "consultar_incidentes",
  "argumentos": {},
  "resultado": "resultado retornado",
  "executada": true,
  "efeito_colateral": false
}
```

Para uma ferramenta que realiza escrita, como `registrar_triagem`, será necessário registrar também se a operação já foi aplicada:

```json
{
  "ferramenta": "registrar_triagem",
  "executada": true,
  "efeito_colateral": true,
  "idempotency_key": "triagem-2026-000123-registro",
  "registro_id": 482,
  "escrita_aplicada": true
}
```

Isso evita que uma execução retomada registre a mesma triagem duas vezes.

---

### Retomada da execução

O checkpoint precisa permitir três situações importantes.

#### Retomar sem repetir efeito colateral

Antes de repetir uma operação de escrita, o sistema deve verificar se aquela operação já foi executada.

Se o checkpoint indicar:

`escrita_aplicada = true`

o agente utiliza o resultado registrado anteriormente em vez de executar novamente a ferramenta.

Assim, uma interrupção não provoca registros duplicados.

#### Receber aprovação humana horas depois

Uma execução poderá ser interrompida aguardando uma decisão humana.

Nesse caso, o checkpoint poderá registrar:

`aguardando_aprovacao_humana = true`

Quando a decisão humana chegar, mesmo horas depois e por outro processo, o sistema poderá carregar o checkpoint pelo `execution_id` e continuar do ponto em que parou.

#### Reproduzir um estado defeituoso

O checkpoint também serve para depuração.

Como serão registrados o modelo, a versão do prompt, a trajetória, as ferramentas utilizadas e seus resultados, será possível carregar um estado anterior e verificar em que ponto ocorreu uma decisão incorreta.

---

## 1.2 O curto prazo e o orçamento da janela

A janela de contexto do modelo é limitada.

A memória de longo prazo é apenas uma das informações que competem por espaço com o restante do contexto.

Neste projeto serão utilizadas cinco fontes principais.

| Fonte | Teto planejado |
|---|---:|
| System prompt e regras procedurais | 1.600 tokens |
| Objetivo e dados do chamado atual | 600 tokens |
| Trajetória recente da execução | 1.200 tokens |
| Trechos recuperados de documentos | 1.000 tokens |
| Memória de longo prazo recuperada | 600 tokens |
| **Total máximo planejado** | **5.000 tokens** |

O limite de 5.000 tokens é uma decisão de projeto e não representa necessariamente o limite máximo suportado pelo modelo.

O objetivo é impedir que uma grande quantidade de memória seja adicionada ao contexto sem controle.

---

### O que acontece quando o limite é ultrapassado

O sistema não deverá simplesmente cortar o final do contexto.

A ordem de prioridade será:

1. system prompt e regras críticas;
2. objetivo e relato atual;
3. resultados recentes de ferramentas;
4. trajetória recente;
5. documentos recuperados;
6. memórias antigas de longo prazo.

Quando o limite de tokens for ultrapassado, o primeiro conteúdo descartado será a memória episódica com menor relevância.

Em seguida poderão ser reduzidos trechos antigos de documentos recuperados.

Partes antigas da trajetória poderão ser resumidas.

Entretanto, algumas informações não poderão ser removidas durante uma execução:

- relato atual;
- objetivo da triagem;
- regras críticas;
- resultados recentes das ferramentas;
- informações sobre operações de escrita já realizadas;
- estado necessário para impedir efeitos colaterais duplicados.

Dessa forma, o sistema evita perder justamente as informações mais recentes e importantes.

---

## 1.3 O longo prazo: as três memórias do agente

A memória de longo prazo será dividida em três tipos: **episódica**, **semântica** e **procedural**.

| Tipo | O que guarda no case | Estrutura | Como é recuperada |
|---|---|---|---|
| **Episódica** | Resumos de triagens anteriores relevantes, erros corrigidos e decisões importantes | Índice por similaridade com metadados | Busca por similaridade com o chamado atual |
| **Semântica** | Fatos estruturados do domínio, como status de incidentes e equipamentos | Chave-valor com timestamp e versão | Consulta pela chave correspondente |
| **Procedural** | Regras de funcionamento do agente | Texto versionado no system prompt | Carregada no início da execução |

---

### Memória episódica

A memória episódica representa experiências anteriores.

O sistema não deverá guardar a conversa inteira de todos os chamados.

Será armazenado apenas um resumo de casos que realmente possam ser úteis posteriormente.

Exemplo:

```json
{
  "episode_id": "ep-00481",
  "timestamp": "2026-09-25T20:15:00",
  "tipo": "divergencia",
  "resumo": "Usuário atribuiu falha ao notebook, mas havia incidente coletivo de rede compatível com a localização informada.",
  "categoria_final": "Rede / Conectividade",
  "ferramentas_relevantes": [
    "consultar_incidentes"
  ],
  "resultado": "triagem concluida"
}
```

Esse tipo de memória poderá ser recuperado por similaridade.

Se um novo chamado apresentar uma situação parecida, o agente poderá receber os episódios anteriores mais relevantes.

Entretanto, um episódio antigo não será tratado automaticamente como verdade sobre o chamado atual.

Ele funciona apenas como experiência anterior que pode ajudar a decisão.

---

### Memória semântica

A memória semântica guarda fatos estruturados do domínio.

Exemplos:

```text
incidente:INC-0031:status = resolvido
equipamento:NB-10203:status = ativo
regra:prioridade:v3 = vigente
```

Essas informações possuem identificadores conhecidos.

Por isso, não existe necessidade de recuperar esses dados por similaridade.

Eles deverão ser consultados diretamente pela chave correspondente.

Cada fato semântico deverá possuir pelo menos:

```text
chave
valor
timestamp
versao
fonte
validade
```

Essa estrutura permite saber qual informação é a mais recente e de onde ela veio.

---

### Memória procedural

A memória procedural representa as regras de funcionamento do agente.

Ela inclui, por exemplo:

- quando consultar incidentes;
- quando consultar equipamentos;
- como tratar um patrimônio inexistente;
- quando encaminhar um caso para atendimento humano;
- quais categorias podem ser utilizadas;
- como classificar prioridade;
- qual é o formato esperado da resposta;
- quando uma ferramenta não deve ser utilizada.

No projeto, essa memória ficará principalmente no `system prompt`.

O agente não poderá alterar suas próprias regras automaticamente.

Uma mudança na memória procedural deverá ser aprovada por uma pessoa e registrada em uma nova versão do prompt.

Isso evita que um erro ocorrido em um único chamado se transforme em uma regra permanente.

---

## 1.4 Quem escreve na memória

A política de escrita deverá utilizar o menor nível de autonomia possível.

Nem tudo o que o agente observa será gravado.

---

### Memória episódica

A criação de episódios será controlada por código depois da conclusão da triagem.

Cada execução poderá produzir:

`0 ou 1 registro episódico`

Cada registro terá aproximadamente:

`150 a 300 tokens`

Serão priorizados casos que contenham:

- divergência entre relato e sistema;
- correção feita por humano;
- erro relevante do agente;
- situação incomum;
- utilização importante de uma ferramenta;
- experiência que possa realmente ajudar em casos futuros.

Chamados simples e repetitivos não precisam necessariamente virar memória permanente.

---

### Memória semântica

O modelo não poderá transformar sozinho qualquer afirmação em fato permanente.

Uma atualização semântica só poderá ser criada quando a informação vier de:

- sistema interno confiável;
- ferramenta validada;
- atualização administrativa;
- correção humana autorizada.

Cada execução poderá produzir aproximadamente:

`0 a 3 fatos semânticos`

Os fatos deverão ser pequenos e estruturados.

---

### Memória procedural

O agente não poderá escrever automaticamente na memória procedural.

Qualquer alteração de regra deverá ser feita ou aprovada por uma pessoa.

Essa regra é importante porque uma interpretação incorreta do agente não pode alterar permanentemente seu comportamento.

---

## O que o agente não guarda

Definir o que não entra na memória é tão importante quanto definir o que entra.

O sistema não deverá guardar informações apenas porque apareceram durante a conversa.

---

### Credenciais e segredos

Nunca deverão ser persistidos em memória de longo prazo:

- senhas;
- tokens;
- chaves de API;
- códigos de autenticação;
- cookies;
- credenciais de VPN;
- segredos de aplicações.

Caso algum desses valores apareça em um relato, ele deverá ser removido antes de qualquer tentativa de persistência.

---

### Dados pessoais desnecessários

Também não serão mantidos em memória de longo prazo dados pessoais que não sejam necessários para o funcionamento do agente.

Exemplos:

- CPF;
- telefone;
- endereço residencial;
- e-mail pessoal;
- nome completo quando não for necessário;
- identificadores pessoais que não tenham relação com a triagem.

Sempre que possível, as memórias episódicas serão armazenadas sem identificação direta do usuário.

---

### Informações externas não verificadas

O agente não poderá transformar automaticamente uma hipótese apresentada pelo usuário em um fato permanente.

Por exemplo:

> "Acho que meu notebook está quebrado."

Essa informação representa a interpretação do usuário.

Ela não significa que o notebook realmente está com defeito.

Somente uma fonte confiável ou validação humana poderá transformar essa hipótese em um fato semântico.

---

### Informações deriváveis

Informações que podem ser recalculadas não precisam ser mantidas permanentemente.

Exemplos:

- contagens intermediárias;
- formatação de uma resposta;
- dados que podem ser obtidos novamente diretamente da fonte oficial;
- valores temporários usados apenas para concluir uma execução.

Armazenar esse tipo de informação aumentaria a quantidade de dados e o risco de inconsistências.

---

### Conversa completa

A conversa completa do usuário não será automaticamente transformada em memória episódica.

Quando um chamado for considerado útil para memória, será produzido apenas um resumo estruturado com as informações necessárias.

---

# Decisão 2 — Como o agente esquece

A memória não pode apenas crescer.

Também é necessário determinar quando uma informação deixa de ser utilizada ou deve ser completamente removida.

O projeto terá três causas diferentes de esquecimento.

| Causa | O que aconteceu | O dado é apagado? | Quando a decisão ocorre |
|---|---|---|---|
| **Contradição** | O fato mudou | Não imediatamente | Durante a leitura |
| **Decaimento** | A informação envelheceu | Pode ser removida ou rebaixada | Rotina periódica |
| **Remoção** | A exclusão foi solicitada | Sim | Sob demanda |

---

## 2.1 Contradição — o fato que mudou

Um mesmo fato pode possuir valores diferentes em momentos diferentes.

Os dois valores podem ter sido verdadeiros, mas em datas distintas.

### Exemplo 1 — Incidente

Em determinado momento:

```text
2026-09-20 10:00
incidente:INC-0031:status = ativo
```

Mais tarde:

```text
2026-09-20 13:40
incidente:INC-0031:status = resolvido
```

As duas informações foram verdadeiras em momentos diferentes.

Se o agente perguntar:

> "Qual é o status atual do incidente INC-0031?"

não deverá deixar que o modelo escolha livremente entre os dois fatos.

Todos os fatos terão um timestamp obrigatório.

A escolha será feita deterministicamente utilizando o registro mais recente.

Regra:

```text
registro_atual = max(registros, key=timestamp)
```

Portanto, nesse exemplo, o resultado atual será:

`resolvido`

---

### Exemplo 2 — Equipamento

Em um primeiro momento:

```text
2026-08-10
equipamento:NB-10203:status = ativo
```

Posteriormente:

```text
2026-09-18
equipamento:NB-10203:status = manutencao
```

Novamente, os dois registros podem ter sido verdadeiros.

Para responder sobre o estado atual do equipamento, o sistema utilizará o registro mais recente.

O registro anterior poderá permanecer como histórico, mas receberá:

```text
vigente = false
```

O registro novo receberá:

```text
vigente = true
```

Assim, a contradição não apaga obrigatoriamente o histórico. Ela define qual informação é válida atualmente.

---

### Registro do descarte por contradição

Quando um fato antigo for recuperado mas não utilizado porque existe um fato mais recente, isso deverá aparecer no log.

Exemplo:

```text
MEMORY_CONFLICT
chave=incidente:INC-0031:status
registro_descartado=ativo
timestamp_descartado=2026-09-20T10:00
registro_utilizado=resolvido
timestamp_utilizado=2026-09-20T13:40
motivo=timestamp_mais_recente
```

Isso é importante para a auditoria.

Sem esse registro, não seria possível saber se o agente:

- encontrou o fato antigo e decidiu descartá-lo; ou
- simplesmente nunca encontrou o fato antigo.

---

## 2.2 Decaimento — o fato que envelheceu

Nem toda informação antiga será contradita por uma informação nova.

Algumas informações apenas perdem utilidade com o tempo.

Por isso, o sistema terá regras de decaimento.

---

### Memória episódica

Após **90 dias**, uma memória episódica começa a perder prioridade na recuperação por similaridade.

Ela não será removida imediatamente.

Sua relevância será reduzida para favorecer acontecimentos mais recentes.

Após **180 dias**, o episódio poderá ser removido caso:

- não tenha sido utilizado recentemente;
- não represente um caso excepcional;
- não tenha sido marcado como importante para avaliação ou auditoria.

A justificativa é que procedimentos, sistemas e problemas de suporte podem mudar com o tempo.

Uma experiência muito antiga pode deixar de representar corretamente a situação atual.

---

### Incidentes

Incidentes possuem uma validade operacional muito menor.

Depois que um incidente for encerrado, ele continuará disponível por um período curto para consultas relacionadas.

Após **7 dias do encerramento**, o incidente deixará de participar das consultas operacionais normais.

Caso seja útil, poderá existir somente como resumo histórico.

Essa decisão reduz o risco de um incidente antigo influenciar indevidamente um chamado novo.

Durante o desenvolvimento do agente já foi observado um problema semelhante.

Em um dos testes, um chamado individual de senha foi associado incorretamente a um incidente de rede no Andar 3.

Uma política de memória deve impedir que incidentes antigos ou não relacionados continuem influenciando casos futuros.

---

### Memória procedural

A memória procedural não será removida simplesmente por idade.

As regras serão versionadas.

Quando uma nova regra for aprovada, a versão anterior deixa de ser a regra ativa, mas poderá permanecer registrada para auditoria e depuração.

---

## 2.3 Remoção — o titular solicitou

A remoção é diferente da contradição e do decaimento.

Quando uma solicitação válida de exclusão ocorrer, o dado deverá ser removido obrigatoriamente de todas as estruturas em que estiver armazenado.

Não basta apagar apenas uma tabela.

---

### Estruturas que devem ser verificadas

Um identificador pode aparecer em diferentes partes do sistema.

A remoção deverá verificar pelo menos:

| Estrutura | O que pode conter |
|---|---|
| Memória episódica | Resumo de atendimento |
| Índice de similaridade | Vetor e metadados do episódio |
| Memória semântica | Fatos ligados ao identificador |
| Memória procedural | Eventual regra que mencione o titular |
| Checkpoints | Relato, argumentos e resultados |
| Logs | Argumentos e resultados de ferramentas |
| Banco de triagens | Resultado final registrado |
| Cache | Informações temporárias recuperadas |
| Arquivos derivados | Exportações ou snapshots |

O checkpoint é especialmente importante porque ele não pertence às três memórias de longo prazo, mas ainda pode armazenar dados do usuário.

Os logs também precisam ser verificados, já que podem conter argumentos enviados para ferramentas.

---

### Memória procedural e remoção

Mesmo a memória procedural precisa ser analisada.

Por exemplo, não seria correto manter permanentemente uma regra como:

> "Quando Pedro abrir um chamado, encaminhar diretamente para o setor X."

Se uma regra foi criada a partir de um caso específico, a regra geral poderá continuar existindo, mas referências diretas ao titular deverão ser removidas.

---

### Procedimento de remoção

A remoção será executada em duas fases.

Primeiro o sistema remove os dados.

Depois outro procedimento realiza uma verificação independente.

O fluxo planejado será:

```text
1. receber o identificador que deve ser removido;
2. localizar todas as estruturas onde ele pode existir;
3. remover ou anonimizar os registros;
4. excluir entradas da memória episódica;
5. excluir vetores e metadados associados;
6. remover fatos da memória semântica;
7. verificar a memória procedural;
8. limpar checkpoints;
9. limpar logs;
10. verificar o banco de triagens;
11. limpar caches;
12. realizar uma nova varredura independente;
13. considerar concluída somente se nenhuma ocorrência permanecer.
```

O ponto mais importante é que a verificação acontece **depois** da remoção.

O sistema não aceitará apenas a resposta do processo que executou a exclusão.

Será feita uma nova busca pelo identificador.

O resultado esperado será semelhante a:

```text
episodica = 0 ocorrencias
indice = 0 ocorrencias
semantica = 0 ocorrencias
procedural = 0 ocorrencias
checkpoints = 0 ocorrencias
logs = 0 ocorrencias
triagens = 0 ocorrencias
cache = 0 ocorrencias
```

Somente depois disso a remoção será considerada concluída.

---

### Caso seja necessário reconstruir o índice

Dependendo da tecnologia utilizada para o índice da memória episódica, pode não existir uma exclusão individual segura.

Nesse caso, será necessária uma reconstrução do índice.

O processo será:

1. remover o registro da fonte principal;
2. gerar novamente o índice sem o dado removido;
3. substituir o índice anterior;
4. executar uma nova busca pelo identificador;
5. confirmar que nenhuma memória relacionada ainda pode ser recuperada.

Enquanto a reconstrução não for concluída, o índice antigo não deverá continuar disponível para uso normal do agente.

---

### Registro da operação de remoção

O sistema poderá manter um log informando que uma remoção foi realizada.

Entretanto, esse próprio log não poderá copiar novamente o dado que foi removido.

Exemplo:

```text
removal_request_id = DEL-2026-0048
resultado = concluido
estruturas_verificadas = 8
ocorrencias_restantes = 0
```

Dessa forma, existe uma evidência de que a operação ocorreu sem recriar o dado que deveria ter sido eliminado.

---

## 2.4 O preço da memória: perda de reprodutibilidade

A introdução da memória altera uma característica importante do agente.

Sem memória de longo prazo, duas execuções iguais tendem a começar com informações semelhantes.

Com memória, o contexto pode mudar ao longo do tempo.

Por exemplo, entre duas execuções:

- um novo episódio pode ter sido armazenado;
- um incidente pode ter mudado de estado;
- um fato semântico pode ter sido atualizado;
- uma memória pode ter sofrido decaimento;
- uma informação pode ter sido removida;
- uma nova regra procedural pode ter sido publicada.

Isso significa que:

> a mesma entrada, utilizando o mesmo modelo e os mesmos parâmetros, pode produzir respostas diferentes em momentos diferentes porque a memória mudou.

Essa diferença não será considerada automaticamente um erro.

Ela é consequência da decisão de permitir que o agente utilize memória.

Para facilitar auditoria e depuração, cada execução deverá registrar pelo menos:

```text
modelo
versao_prompt
timestamp
execution_id
memorias_recuperadas
versoes_dos_fatos_semanticos
versao_ou_snapshot_da_memoria
```

Quando for necessário realizar um teste completamente reproduzível, poderá ser utilizado um snapshot congelado da memória.

Assim, será possível separar duas causas de mudança:

1. mudança no comportamento do modelo;
2. mudança no conteúdo disponível na memória.

---

# 3. Política final de memória

A política de memória deste agente segue o princípio de que **lembrar de tudo não é o objetivo**.

A memória de curto prazo deverá armazenar o estado necessário para concluir ou retomar corretamente uma execução.

A memória de longo prazo deverá armazenar apenas informações com valor provável para atendimentos futuros.

A memória episódica armazenará experiências selecionadas.

A memória semântica armazenará fatos estruturados, versionados e provenientes de fontes confiáveis.

A memória procedural armazenará as regras aprovadas que orientam o comportamento do agente.

O agente não poderá transformar automaticamente qualquer informação recebida em memória permanente.

---

# 4. O que o agente não guarda — e o que ele perde quando perde

O agente deliberadamente não guardará:

- senhas;
- credenciais;
- tokens;
- chaves de API;
- dados pessoais desnecessários;
- hipóteses do usuário como se fossem fatos;
- conversas completas quando um resumo é suficiente;
- informações externas não verificadas;
- estados intermediários que podem ser recalculados;
- regras criadas automaticamente a partir de um único atendimento.

Essa decisão reduz riscos de segurança, privacidade, inconsistência e crescimento desnecessário da memória.

Quando um **checkpoint** é eliminado, o agente perde a capacidade de retomar exatamente aquela execução de onde ela parou.

Quando uma **memória episódica** é removida por decaimento, o agente perde a possibilidade de utilizar aquele atendimento como experiência anterior.

Quando um fato da **memória semântica** é substituído por contradição, o valor antigo deixa de representar o estado atual, embora possa permanecer como histórico.

Quando uma regra da **memória procedural** é substituída, a versão antiga deixa de orientar novas execuções.

Quando ocorre uma **remoção solicitada**, o sistema aceita perder definitivamente aquela informação e qualquer benefício que poderia obter dela.

Essa perda é intencional.

No projeto, uma informação só deve permanecer na memória enquanto for útil, necessária, confiável e permitida.

---

# 5. Conclusão

A memória do agente será dividida entre curto prazo e longo prazo.

No curto prazo, o checkpoint permitirá retomar execuções, aguardar decisões humanas e impedir a repetição de efeitos colaterais.

No longo prazo, serão utilizadas três formas diferentes de memória:

- episódica, para experiências anteriores;
- semântica, para fatos estruturados;
- procedural, para regras de comportamento.

O uso da memória será limitado por um orçamento de contexto, evitando que informações antigas ocupem espaço necessário para o chamado atual.

O esquecimento será tratado de três formas distintas:

- **contradição**, quando um fato novo substitui o estado atual de um fato anterior;
- **decaimento**, quando uma informação perde relevância com o tempo;
- **remoção**, quando uma informação precisa ser eliminada obrigatoriamente de todas as estruturas.

A política adotada busca permitir que o agente aproveite conhecimento anterior sem transformar todo atendimento em memória permanente.

O princípio final é:

> o agente deve lembrar apenas do que continua sendo útil, confiável, necessário e permitido.
