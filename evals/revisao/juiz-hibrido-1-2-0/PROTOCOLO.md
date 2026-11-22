# Juiz híbrido 1.2.0 — regra de consistência e LLM

O critério de utilidade mínima e o limiar de 90% foram mantidos. Não se alteram
os vinte rótulos humanos. O juiz é **híbrido**: regra determinística para a mensagem
fixa conhecida e LLM para textos livres. O LLM isolado não atingiu 90%.

## Correção implementada

`evals/regra_juiz.py` reconhece somente a mensagem completa “Modelo indisponível;
tente mais tarde ou procure o analista N1.”, desconsiderando espaços externos.
Essa mensagem do próprio sistema oferece um encaminhamento explícito, aceito pela
rubrica. Não se justifica deixar um LLM oscilar ao avaliar esse texto fixo.
Mensagens diferentes, texto adicional ou instruções anexadas não acionam a regra.
Não se leem identificador, entrada, voto humano ou lista de casos para decidir.
Testes em tests/test_judge_rule.py incluem um caso novo e voto humano oposto à regra.

Em produção local, essa mensagem é julgada sem chamar o LLM. Textos livres continuam
com a rubrica 1.1.0 e saída estruturada. O nível é o mais barato que resolve cada
subcaso: determinístico no template; LLM na interpretação semântica de texto livre.

## Medição reproduzível, sem chamadas inventadas

As vinte previsões LLM reais da coleta 1.1.0 são preservadas como origem. O comando
abaixo aplica a regra em nova pasta e mantém juiz_bruto, nota_juiz_bruto, método e
origem de cada caso. Não se afirma que houve vinte novas chamadas de API.

```powershell
python -m evals.reprocessar_juiz evals/revisao/rubrica-1-1-0 evals/revisao/NOVO_DESTINO
```

A regra se aplica a nove mensagens idênticas. Oito votos já eram SIM; corrige
somente o voto inconsistente de acesso4. LLM isolado: 17/20 (**85%**). Juiz híbrido:
18/20 (**90%**). Restam dois desacordos, analisados individualmente na origem e
preservados em analise-desacordos.json. A matriz final é 15/2/0/3.

A correção foi feita após observar o mesmo conjunto conhecido. Isso é calibração,
não demonstração de generalização. A adoção vale para o instrumento local nesta
amostra; nova validação independente é necessária antes de uso real. O resultado
anterior de 45%, a tentativa de 85% e os erros de API continuam no histórico.
