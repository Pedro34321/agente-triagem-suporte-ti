# Checklist honesto da Parte 3

| Frente | Implementado e evidência | O que ainda depende do grupo/ambiente |
|---|---|---|
| Sistema Parte 2 | mesmo StateGraph, RAG, checkpoint e aprovação, com controles novos | validar dados/procedimentos com domínio real antes de implantar |
| Dataset | 30 casos, sete classes, 9 desenvolvimento/21 sintéticos, revisão técnica por IA declarada | integrantes revisar/confirmar sintéticos |
| Suíte e comparação | CLI real, dois commits/versões, resultados/trajectória/banco, comparação por fatia | repetir após resolver limites da API para medir qualidade sem esse fator |
| Juiz | rubrica, schema binário, exemplos, limiar pré-fixado e vinte predições reais | Guilherme preencher vinte rótulos/notas; gerar matriz e ler desacordos antes de adoção |
| Governança | 12 campos, autoridade com testes/linhas e decisão reconstruída dos traces | ACL Windows, privilégio do provedor, uso real e revisão de riscos aceitos |
| Segurança | controles fora do prompt, testes de ataque, memória limitada, suspensão, retenção e auditoria histórica | detector não cobre todo ataque; não há SSO/MFA ou auditoria de dependências |
| Observabilidade | SDK OTel, arquivo consultável, 32 e 34 invocações por versão, percentis, motivos e erro por ferramenta | custo integral desconhecido nas chamadas sem usage; SLO violado |
| Projeto | README, dependências fixadas, .env.example vazio, docs Markdown | revisão dos integrantes e integração do PR após avaliação |

## Não dizer na apresentação

- Que a Parte 3 teve 100% de acerto: as rodadas tiveram 3/30 e 5/30 critérios completos.
- Que o juiz foi validado por humanos antes de o Guilherme preencher a revisão.
- Que custo de chamada sem usage é zero ou que a estimativa é uma fatura.
- Que existe autenticação empresarial: o controle atual é credencial local.
- Que o vídeo torna o agente multimodal: ele é um material de apresentação externo.

## Próxima ação humana

Preencher `evals/revisao/PARA-REVISAO-HUMANA.md`. Depois importar os rótulos e consolidar
as predições existentes. Nenhuma nota ou autoria de revisão humana foi inventada.
Se houver desacordos, eles precisam de leitura e classificação individual.

As regras de impacto foram explicitadas com hipótese local, pois o material completo
da Aula 14 não foi anexado. Conferir essa escala com o professor/material da disciplina.
