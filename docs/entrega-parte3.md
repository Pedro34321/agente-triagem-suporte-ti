# Guia da entrega — Parte 3

Entrega acadêmica do sistema local de triagem, versão 3.1.0. As quatro frentes
obrigatórias estão implementadas e documentadas, incluindo resultados negativos.
Isso não constitui aprovação para produção. A avaliação assistida por IA e a
confirmação da revisão por intermédio do usuário estão explicitadas nos arquivos.

| Frente | Implementado e evidência | O que ainda depende do grupo/ambiente |
|---|---|---|
| Sistema Parte 2 | mesmo StateGraph, RAG, checkpoint e aprovação, com controles novos | validar dados/procedimentos com domínio real antes de implantar |
| Dataset | 30 casos, sete classes, 9 desenvolvimento/21 sintéticos, revisão técnica por IA declarada | sem dados de produção ou revisão humana independente dos sintéticos |
| Suíte e comparação | CLI real, dois commits/versões, resultados/trajectória/banco, comparação por fatia | repetir após resolver limites da API para medir qualidade sem esse fator |
| Juiz | vinte votos com razões e revisor, matriz 6/11/0/3, concordância 45%, onze desacordos analisados individualmente | não adotado: abaixo do limiar de 90%; revisão assistida por IA, não cega |
| Governança | 12 campos, autoridade com testes/linhas e decisão reconstruída dos traces | ACL Windows, privilégio do provedor, uso real e revisão de riscos aceitos |
| Segurança | controles fora do prompt, testes de ataque, memória limitada, suspensão, retenção e auditoria histórica | detector não cobre todo ataque; não há SSO/MFA ou auditoria de dependências |
| Observabilidade | SDK OTel, arquivo consultável, 32 e 34 invocações por versão, percentis, motivos e erro por ferramenta | custo integral desconhecido nas chamadas sem usage; SLO violado |
| Projeto | README, dependências fixadas, .env.example vazio, docs Markdown e testes automatizados | requer chave própria com acesso/cota para repetir as chamadas reais |

## Não dizer na apresentação

- Que a Parte 3 teve 100% de acerto: as rodadas tiveram 3/30 e 5/30 critérios completos.
- Que o juiz foi aprovado para uso: sua concordância ficou abaixo do limiar.
- Que os pareceres são uma revisão cega independente: foram assistidos por IA.
- Que custo de chamada sem usage é zero ou que a estimativa é uma fatura.
- Que existe autenticação empresarial: o controle atual é credencial local.
- Que o vídeo torna o agente multimodal: ele é um material de apresentação externo.

## Revisão e autoria

Guilherme dos Santos Medeiros conferiu os vinte pareceres apresentados na conversa,
segundo confirmação do usuário, que solicitou incorporá-los. As sugestões e razões
foram redigidas por IA. O registro não é assinatura digital nem comprovação direta
da identidade do revisor. Proveniência em `evals/revisao/PROVENIENCIA-REVISAO.md`.
A análise dos onze desacordos foi feita por Codex (IA), com autoria própria declarada.

## Conferência local, sem novas chamadas pagas

Na raiz do repositório, com ambiente instalado conforme o README:

```powershell
python -m pytest -q
python -m evals.importar_rotulos evals/revisao/PARA-REVISAO-HUMANA.md
python -m evals.calibrar_juiz --consolidar
python -m evals.comparar evals/resultados/baseline-3-0-0 evals/resultados/controles-3-1-0
python -m evals.metricas evals/resultados/controles-3-1-0
python -m scripts.relatorio_parte3
```

Esses comandos verificam testes locais e evidências existentes. Rodar novamente
`evals.rodar` ou `evals.calibrar_juiz --avaliar` exige API real e pode gerar custo.

## Como apresentar os resultados

- Baseline: 3/30 critérios completos (10%); controles: 5/30 (16,7%).
- Fatia segurança: 2/3 → 3/3 nos três ataques medidos, sem alegar defesa geral.
- Juiz: 45% de concordância, abaixo de 90%; avaliado e não adotado.
- SLO operacional: violado nas duas versões; manter demonstração acadêmica e
  investigar limites/ritmo da Mistral antes de repetir a medição.
- Mensagem com encaminhamento ao N1 pode ser útil pela rubrica e continuar sendo
  falha técnica da execução. Os números das rodadas não foram alterados por esse voto.

O enunciado aceita expressamente juiz não adotado e SLO violado quando medidos e
reportados. Não é necessário transformar resultados negativos em sucesso para entregar.

## Como entregar

Enviar o link do repositório na versão que contém a Parte 3. Enquanto o PR #2 não
estiver integrado à main, usar o link direto da branch `codex/parte-3`, pois a main
pode mostrar somente as partes anteriores. Não anexar `.env.local`, `.runtime/`,
credenciais, bancos pessoais ou ambiente virtual. O README aponta para as evidências.

A escala de impacto foi alinhada à análise do grupo em exercicios/aula14-respostas.md,
preservada ao integrar a main. ASI03 e ASI01 são priorizados entre os riscos máximos.
