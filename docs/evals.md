# Avaliação — Parte 3

## Dataset e execução

`evals/dataset.json` v1.0.0 contém 30 casos: 9 de desenvolvimento (incluindo todos
os casos demonstrados na Parte 2), 21 sintéticos e nenhum de produção. Sete classes
têm mais de um caso: acesso, rede, hardware, orientação, coleta, recusa e segurança.
Cada caso declara entrada, esperado, origem, classe, motivo e revisão. A revisão
técnica dos sintéticos foi feita por Codex, explicitamente identificado como IA;
a revisão dos integrantes ainda precisa ocorrer. Não foi atribuída uma assinatura humana.

`python -m evals.rodar --versao 3.1.0 --rodada NOME_NOVO` invoca `python -m src.main`,
exatamente a CLI do README, em subprocessos. Cada caso usa um banco isolado. Em casos
de ação, a suíte consulta o mundo antes e depois, aprova/edita por roteiro e repete
a aprovação. Nenhuma resposta mock é usada nessas rodadas. Testes locais separados
usam doubles para atacar controles de maneira previsível.

## Propriedades e níveis

| Propriedade | Nível | Conferência | Por que esse nível |
|---|---|---|---|
| Categoria, prioridade, suficiência e pergunta | determinístico | esperado vs objeto real | igualdade/schema bastam para esses rótulos |
| Consulta e ausência/presença de escrita | trajetória | nomes de spans execute_tool | só a resposta não prova qual ferramenta executou |
| Zero escrita antes da aprovação, uma depois e duplicata | resultado | SELECT count(*) + id efetivo | o agente pode afirmar sucesso sem alterar o banco |
| Utilidade do próximo passo | juiz LLM, ainda não adotado | rubrica binária e nota | há várias redações válidas, igualdade lexical não mede utilidade |

## Duas versões reais

A versão 3.0.0 mantém a lógica da Parte 2 com instrumentação e constitui a baseline.
A 3.1.0 acrescenta autorização local/grant de escrita, filtro de entrada hostil,
minimização da memória e exigência de localização explícita. Os hashes dos commits
de execução estão nos resumos. Não foi trocado o dataset entre as rodadas.

- `evals/resultados/baseline-3-0-0/resumo.json`: **3/30**, 10,0%.
- `evals/resultados/controles-3-1-0/resumo.json`: **5/30**, 16,7%.
- `evals/resultados/comparacao.txt`: tabela por classe, diferença de **+6,7 pp** na média micro.

Na fatia segurança: 2/3 (66,7%) para 3/3 (100%). Essa diferença é compatível com o
novo bloqueio determinístico dos três textos hostis, mas não prova defesa geral
contra injeção. A maioria dos demais casos falhou por erro 429 do provedor. Portanto,
não é válido concluir que a qualidade semântica melhorou com base na média global.
O serviço não está apto a promoção operacional: o SLO foi violado nas duas versões.

## Juiz e revisão humana

Rubrica v1.0.0 em `src/prompts/juiz.txt`: a resposta permite entender o próximo passo?
Aprova classificação compreensível, pergunta específica ou recusa útil; reprova
resposta vaga/contraditória. Há exemplo positivo e negativo. Schema `Judgment` exige
booleano e nota. O juiz não mede schema, segurança nem efeito no banco.

O limiar de adoção **>=90%** foi registrado em `evals/politica.json` antes das rodadas.
Vinte saídas reais foram selecionadas, nove da Parte 2 e onze da baseline. O documento
`evals/revisao/PARA-REVISAO-HUMANA.md` deve ser preenchido pelo Guilherme, conforme
indicação do usuário. O nome não foi preenchido como se a revisão já tivesse ocorrido.

**LACUNA:** vinte rótulos humanos, notas e identificação do revisor pendentes. A matriz
de concordância permanece nula e o juiz **não é adotado** enquanto isso não for resolvido.
Predições do modelo, inclusive falhas de API, ficam separadas em `evals/revisao/`.

Após a revisão:

```powershell
python -m evals.importar_rotulos evals/revisao/PARA-REVISAO-HUMANA.md
python -m evals.calibrar_juiz --consolidar
```

A consolidação reutiliza as predições e não chama novamente a API. Havendo desacordo,
cada caso deve ser lido e classificado como defeito do juiz, da rubrica ou do rótulo
humano. O relatório não promove automaticamente um juiz com desacordos não analisados.
Sem rótulos humanos não há percentual nem matriz legítimos para apresentar.

## Limites da medição

Amostra pequena, sintética/de desenvolvimento, sem teste cego e sem variabilidade
entre múltiplas repetições do mesmo caso. A cota do provedor é um fator de confusão
observado, não removido dos resultados. Custos são estimativas por usage, nunca fatura.
