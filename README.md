# Agente Inteligente para Triagem de Chamados de Suporte de TI

## Integrantes

- Pedro Henrique Macedo Cunha
- Guilherme dos Santos Medeiros 

## Problema

Analistas de suporte gastam tempo interpretando chamados incompletos, coletando informações adicionais e classificam manualmente a categoria, prioridade e encaminhamento correto de cada solicitação.

## Parte 3 — avaliação, segurança e observabilidade

Versão do sistema: **3.1.0**. O grafo da Parte 2 foi mantido e recebeu controles e
traces OpenTelemetry. Instale o requirements.txt atualizado no ambiente Python 3.12.
Provedor ativo: Mistral, com credencial local já configurada neste computador.
Nenhuma chave é incluída na entrega. Em outro computador, configure MISTRAL_API_KEY
em `.env.local`, a partir do seu acesso ao provedor; `.env.example` contém só nomes.

Do zero, no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.main iniciar "Senha incorreta no meu e-mail corporativo." --caso exemplo-parte3
python -m src.main retomar demo:principal:exemplo-parte3 aprovar
```

A CLI gera um segredo de revisão em `.runtime/reviewer.json`, ignorado pelo Git, e o
usa para o principal `revisor-local`. Não exiba nem publique esse arquivo. Isso prova
posse da credencial local, não login corporativo/MFA. Chamadas Python a App.resume
sem credencial/identidade corretas são bloqueadas. Quem tem acesso aos arquivos como
operador continua capaz de aprovar: limitação aceita apenas no cenário acadêmico.

### Avaliação reproduzível e comparação

```powershell
python -m evals.rodar --versao 3.1.0 --rodada minha-rodada-nova
python -m evals.comparar evals/resultados/baseline-3-0-0 evals/resultados/controles-3-1-0
python -m evals.metricas evals/resultados/controles-3-1-0
python -m pytest -q
python -m pytest tests/test_security.py tests/test_retention.py tests/test_redaction.py -q
```

A primeira linha faz chamadas reais pagas à Mistral, em bancos isolados, e precisa de
acesso/cota. As demais conferem evidências existentes ou controles com doubles.
Para repetir **exatamente a baseline**, use o commit `2fdc11d` em outro checkout e rode
`python -m evals.rodar --versao 3.0.0 --rodada OUTRO_NOME`. O comando valida a versão
do código; não permite trocar apenas o rótulo da rodada. Não reutilize uma pasta de
resultado existente. As duas rodadas entregues têm o mesmo hash de dataset.

**Resultado observado:** 3/30 na baseline e 5/30 com controles. Os erros 429 dominam
essas execuções. O SLO de 90% foi violado nas duas versões. Não confundir esses números
com os nove casos da Parte 2 nem declarar o agente pronto para produção. Detalhes,
fatias, fatores de confusão e arquivos-fonte em [evals.md](docs/evals.md).

### Como ver os traces e aplicar retenção

```powershell
Get-ChildItem .runtime/traces/*.jsonl
python -m scripts.ver_traces CAMINHO_DO_TRACE.jsonl
python -m scripts.retencao --dias 30
python -m src.main expirar
```

As evidências versionadas ficam em `evals/resultados/<rodada>/traces/`. Cada arquivo
é um trace OpenTelemetry JSONL com raiz invoke_agent, chamadas chat e execute_tool.
Entrada, fontes, modelo, prompts, resultado e aprovação ficam no mesmo trace.
Retomadas têm outro trace e o mesmo gen_ai.conversation.id. Retenção e expiração são
comandos explícitos, ainda sem agendamento automático. Não removem backups nem Git.
Para suspender, defina `TRIAGEM_SUSPENDED=1` no ambiente antes de executar a CLI.

### Revisão humana do juiz

As vinte respostas em `evals/revisao/PARA-REVISAO-HUMANA.md` estão rotuladas: 17 SIM
e 3 NÃO. Guilherme conferiu os pareceres assistidos por IA, conforme confirmação do
usuário. A origem e os limites dessa confirmação estão em
[PROVENIENCIA-REVISAO.md](evals/revisao/PROVENIENCIA-REVISAO.md).
Concordância juiz × humano: **9/20 (45%)**, abaixo do limiar prévio de 90%.
O juiz foi avaliado e **não adotado**. Matriz completa em [evals.md](docs/evals.md);
os onze desacordos foram lidos individualmente em
[DESACORDOS.md](evals/revisao/DESACORDOS.md), com análise técnica por IA declarada.

```powershell
python -m evals.importar_rotulos evals/revisao/PARA-REVISAO-HUMANA.md
python -m evals.calibrar_juiz --consolidar
```

Para coletar novamente as vinte predições do juiz, com custo de API e espaçamento:
`python -m evals.calibrar_juiz --avaliar --intervalo 35`. Não é necessário repetir
essa coleta apenas porque chegaram os rótulos humanos. A consolidação preserva as
análises vinculadas aos votos e ao hash do texto; mudanças invalidam análises antigas.
Uma nova coleta exige nova leitura dos desacordos antes de qualquer adoção.

### Documentação da Parte 3

- [Avaliação](docs/evals.md)
- [Model card e reconstrução da decisão](docs/model-card.md)
- [Segurança, autoridade e dados](docs/seguranca.md)
- [Plano, métricas e SLO](docs/observabilidade.md)
- [Mudanças e commits](docs/mudancas.md)
- [Escopo das frentes opcionais](docs/opcionais.md)
- [Guia da entrega e limitações](docs/entrega-parte3.md)

Os comandos e resultados abaixo pertencem à **Parte 2** e permanecem como histórico.

## Parte 2 — como rodar

Python 3.12. Execute na raiz do repositório (Windows/PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.main iniciar "Não consigo entrar no e-mail corporativo: senha incorreta." --caso exemplo1
```

Configure `MISTRAL_API_KEY` no `.env.local` local, ignorado pelo Git. O ambiente preparado
para este trabalho já contém esse arquivo; não o envie nem copie para a entrega.
`.env.example` lista somente nomes. Provedor padrão: Mistral; modelo `ministral-8b-2512`,
alterável por `LLM_MODEL`. OpenAI é opcional com `LLM_PROVIDER=openai` e `OPENAI_API_KEY`.
Não é necessário recriar `dados/suporte.db`: ele contém fixtures da Parte 1.
Em Linux/macOS, ativação: `source .venv/bin/activate`.

**Validação:** 10 testes locais aprovados, 10/10 perguntas de recuperação e 9/9 casos
reais conferidos com Ministral 8B, incluindo os seis obrigatórios. Evidências em
`logs/parte2/`. Os critérios automáticos não substituem revisão do texto pelo grupo.

## Como usar

A entrada é o relato em texto livre. Sem texto no comando, a CLI pergunta o relato.
Metadados opcionais `--usuario`, `--sessao`, `--caso` identificam a conversa.
O retorno é JSON validado com resultado, fontes e suficiência; informação insuficiente
produz perguntas, e assuntos sem fonte produzem recusa. Para complementar um relato
incompleto, repita `iniciar` com os mesmos identificadores e o novo texto.

Se aparecer `aguardando_aprovacao`, confira `pendencia.argumentos` e a consequência.
Nenhum registro foi criado nesse ponto. Em outra execução do programa:

```powershell
python -m src.main retomar demo:principal:exemplo1 aprovar
python -m src.main retomar demo:principal:exemplo1 aprovar
```

A segunda aprovação retorna o mesmo id e `ja_existia=true`. Alternativas:

```powershell
python -m src.main retomar demo:principal:outro editar --prioridade Alta --equipe "Suporte N2"
python -m src.main retomar demo:principal:outro rejeitar
python -m src.main expirar
python -m src.main esquecer demo
```

O prazo é 24 horas. `expirar` encerra pendências vencidas; não há execução automática
desse comando. Mesmo sem a rotina, aprovação atrasada não registra. O comando esquecer
remove os dados operacionais daquele usuário local; detalhes e limites em `docs/memoria.md`.
Use novo caso para uma nova ação depois de registrar. Interface local de demonstração,
sem autenticação: somente dados fictícios e operador de confiança.

## Verificação e evidências

```powershell
python -m pytest -q
python conferir_grafo.py
python -m scripts.avaliar_local
python -m scripts.documentar_grafo
python -m scripts.demonstrar
python -m scripts.conferir_casos
python -m scripts.ablacao
```

Os quatro primeiros e `conferir_casos` não chamam a API. `demonstrar` e `ablacao` fazem chamadas pagas e requerem
saldo. `demonstrar` gera nove casos (incluindo os seis obrigatórios), saída completa,
data/commit/modelo/prompts e aprovação editada/repetida. Ele atualiza `docs/io.md` e
o exemplo principal deste README. Para vínculo exato, execute após commit do código.
`ablacao` compara um prompt com e sem uma frase. Falhas de API nunca viram logs de sucesso.

- [Arquitetura e estado](docs/arquitetura.md)
- [Case e complemento](docs/case.md)
- [RAG e dez perguntas](docs/rag.md)
- [Memória](docs/memoria.md)
- [Aprovação humana](docs/humano.md)
- [Plano de prompts](docs/prompts.md)
- [Contrato e exemplos](docs/io.md)
- [Pendências e cobertura do enunciado](docs/entrega-parte2.md)

Os logs antigos `.txt` são da Parte 1. Novas evidências ficam em `logs/parte2/`;
dados operacionais e checkpoints ficam em `.runtime/`, sem versionamento.
`src/tools.py` e `src/database.py` são módulos legados da Parte 1; a CLI atual usa
`src/knowledge.py` e `src/storage.py`. O histórico anterior foi preservado.
<!-- EXEMPLO_REAL -->
## Exemplo principal executado

Não consigo entrar no meu e-mail corporativo. Quando coloco minha senha, aparece que ela está incorreta.

```json
{
  "resultado": "Falha individual de acesso ao e-mail corporativo devido à senha incorreta.",
  "fontes": [
    {
      "id": "KB-ACESSO",
      "trecho": "Falha individual de senha ou conta: Acesso / Conta, prioridade Média, Suporte N1. Não pedir a senha. Exceção: suspeita de comprometimento de conta deve ser encaminhada ao Suporte N2 com prioridade Alta; nunca redefinir credenciais automaticamente."
    }
  ],
  "suficiente": true,
  "categoria": "Acesso / Conta",
  "prioridade": "Média",
  "encaminhamento": "Suporte N1",
  "perguntas": [],
  "registrar": true,
  "motivo_termino": "registrado",
  "thread_id": "demo:1792454013396141800:caso_simples",
  "registro_id": 1,
  "ja_existia": false,
  "pendencia": null
}
```
