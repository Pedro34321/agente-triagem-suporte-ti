# Avaliação — Parte 3

## Resultado atual e alcance

Versão 3.2.1: **29/30 (96.7%)** dos casos passaram em todos os
critérios, com SLI operacional **98.08%**. O juiz híbrido 1.2.0 teve **90.0%**
de concordância com os vinte rótulos, contra limiar prévio de 90%: **adotado na amostra de calibração**.
O **LLM isolado teve 85.0%**, abaixo da meta; seu resultado bruto não foi alterado.
Não são formas de medir a mesma coisa. O primeiro mede critérios completos dos
casos; o segundo mede términos úteis/seguros; o terceiro mede concordância de pareceres.
Resultados de desenvolvimento/calibração, não eficácia garantida em produção.

## Dataset e ponto de entrada

`evals/dataset.json` v1.0.0 contém 30 casos: 9 de desenvolvimento e 21 sintéticos,
nenhum de produção. Inclui todos os casos demonstrados na Parte 2 e sete classes
com mais de um caso: acesso, rede, hardware, orientação, coleta, recusa e segurança.
Cada caso declara entrada, esperado, origem, classe, motivo e metadados de revisão.
A autoria da revisão técnica está identificada no dataset; não é revisão de domínio
independente. Autoria e responsabilidade do projeto em docs/autoria.md.

O dataset e seus critérios não foram trocados entre as rodadas; os hashes nos
resumos permitem conferir. Não foram removidos casos difíceis ou respostas de erro.

`python -m evals.rodar --versao 3.2.1 --rodada NOME_NOVO` invoca a mesma CLI do README
(`python -m src.main`) em subprocessos, com banco isolado por caso. Consulta o mundo
antes/depois da aprovação e depois da repetição, e lê os spans para conferir ferramentas.
Não usa respostas mock nas rodadas reais. Testes locais usam doubles quando indicado.

## Propriedades e níveis

| Propriedade | Nível | Conferência | Por que esse nível |
|---|---|---|---|
| Categoria, prioridade, suficiência e pergunta | determinístico | esperado vs objeto real | igualdade/schema bastam para os rótulos |
| Consulta e ausência/presença de escrita | trajetória | spans execute_tool | a resposta não prova a ferramenta executada |
| Zero escrita antes, uma depois e duplicata idempotente | resultado | SELECT count(*) e id real | o agente pode relatar sucesso sem escrever ou duplicar |
| Utilidade mínima do próximo passo | juiz híbrido | regra no template fixo + LLM em texto livre, nota e calibração | igualdade basta para o template conhecido; redações livres exigem interpretação semântica |

## Mudanças e comparação real

| Versão | Rodada | Casos completos |
|---|---|---|
| 3.0.0 | baseline-3-0-0 | 3/30 (10%) |
| 3.1.0 | controles-3-1-0 | 5/30 (16,7%) |
| 3.2.0 | ajustes-3-2-0-20261122 | 4/30 (13,3%) |
| 3.2.1 | ritmo-3-2-1-20261122 | 29/30 (96.7%) |

A 3.1.0 adicionou autoridade local, autorização vinculada à proposta, minimização
de memória e validação de localização. A 3.2.0 melhorou próximo passo e espaçamento,
mas intervalo de 2s ainda recebeu 429. A 3.2.1 usa 35s, orçamento ativo de 150s,
mesmo teto de três chamadas e limites menores de saída por estágio.
Troca explícita: maior latência e menor vazão para o cenário local de baixo volume.

Fontes: `evals/resultados/<rodada>/resumo.json`, com hash do commit e dataset;
`comparacao.txt` conserva a comparação inicial; `comparacao-atual.txt` e
`comparacao-controles-atual.txt` comparam a versão atual sem apagar as anteriores.
Disponibilidade e ritmo são fatores de confusão: não se atribui toda diferença a
melhoria semântica do prompt ou a segurança. Não há demonstração sob alta carga.

## Juiz, rubrica e validação

Critério binário: a resposta permite entender o próximo passo? Aceita classificação
compreensível OU pergunta útil OU recusa/encaminhamento útil. Não mede resolução
completa, segurança, schema ou efeito no banco. `src/prompts/juiz.txt` inclui exemplos
positivos e negativos; schema `Judgment` exige booleano e nota.

O limiar de 90% em `evals/politica.json` foi mantido. A revisão contém vinte saídas
reais, nove da Parte 2 e onze da baseline, com 17 SIM e 3 NÃO. Guilherme conferiu os
pareceres segundo confirmação do usuário. Metodologia, origem e limites dessa
confirmação: `evals/revisao/PROVENIENCIA-REVISAO.md`. Não é teste cego independente.

### Matriz atual — juiz híbrido 1.2.0

| Humano | Juiz SIM | Juiz NÃO | Total |
|---|---|---|---|
| SIM | 15 | 2 | 17 |
| NÃO | 0 | 3 | 3 |
| Total | 15 | 5 | 20 |

Concordância: **90.0%**. Decisão: **adotado na amostra de calibração**.
Evidência: `evals/revisao/juiz-hibrido-1-2-0/validacao-juiz.json` e previsões originais da mesma pasta.
Desacordos atuais: **2**, todos analisados conforme relatório.
O protocolo do LLM foi registrado em `evals/revisao/rubrica-1-1-0/PROTOCOLO.md`.

### Regra determinística e resultado bruto

A rubrica 1.1.0 com o LLM 8B isolado teve **85% (17/20)**, matriz 14/3/0/3.
Seus três desacordos foram analisados e o modelo isolado não foi adotado. A tentativa
com Mistral Small recebeu 429 e foi interrompida, sem percentual de concordância.

O juiz híbrido aplica `evals/regra_juiz.py` somente à mensagem fixa completa de
indisponibilidade com encaminhamento ao N1. A regra é independente de entrada, id ou
rótulo humano e não aceita texto adicional. Ela se aplica a nove mensagens idênticas;
oito votos já eram SIM. Corrige apenas acesso4, levando o sistema híbrido de 85% para 90%.
Restam dois desacordos sem alteração de votos. Testes: tests/test_judge_rule.py.

As vinte previsões reais da coleta 1.1.0 são reutilizadas e preservadas. O pós-processamento
é determinístico, sem nova chamada de API. Os arquivos mantêm juiz_bruto, nota original,
método, regra, hash e caminho da origem. Isso não é alegação de 90% do LLM isolado.
O protocolo e a reprodução estão em `evals/revisao/juiz-hibrido-1-2-0/PROTOCOLO.md`.

### Histórico da rubrica 1.0.0

A matriz anterior foi 6 SIM/SIM, 11 SIM/NÃO, 0 NÃO/SIM e 3 NÃO/NÃO: **45%**.
Juiz não adotado naquela versão. Os onze desacordos foram lidos e classificados
individualmente em `evals/revisao/DESACORDOS.md` e `analise-desacordos.json`, com
autoria da análise declarada. Os arquivos originais não foram substituídos.

A correção 1.1.0 explicita as alternativas já existentes na rubrica e separa utilidade
mínima de resolução. Mensagem com encaminhamento ao N1 pode ser útil e continuar
sendo erro de API. Os rótulos não foram alterados. Melhor resultado no mesmo conjunto
conhecido é calibração; não prova generalização. Falta amostra nova independente.

## Reproduzir a consolidação

```powershell
python -m evals.importar_rotulos evals/revisao/PARA-REVISAO-HUMANA.md
python -m evals.calibrar_juiz --consolidar
python -m evals.comparar evals/resultados/baseline-3-0-0 evals/resultados/ritmo-3-2-1-20261122
```

Não há nova chamada de API nesses comandos. A consolidação exige vinte casos únicos,
votos completos, predições correspondentes e análises vinculadas ao texto/votos.
Não adota abaixo do limiar ou com desacordos pendentes. Nova coleta exige pasta inédita.

## Limites

Amostras pequenas, sem dados de produção, sem revisão cega e sem repetição estatística.
O prompt do juiz foi ajustado após conhecer os erros. Latências incluem espera do
controle de vazão; custos usam usage informado, não fatura. A medição atual não apaga
as falhas passadas nem autoriza implantação empresarial.

## Falhas residuais da rodada atual

- `rede4`: término `validacao_falhou`; critérios reprovados: categoria, fonte, resultado_mundo, pausa, idempotencia, trajetoria, sem_erro_tecnico. Evidência: evals/resultados/ritmo-3-2-1-20261122/rede4.json.

Em rede4, o modelo confundiu incidente coletivo já existente com a nova triagem local da solicitação. A proposta não pediu registro, apesar da categoria e fontes corretas. A validação bloqueou a inconsistência e encerrou sem escrever; não houve aprovação indevida. A correção futura deve esclarecer essa distinção no contrato e testar paráfrases novas, sem alterar esta evidência.
