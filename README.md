# Agente Inteligente para Triagem de Chamados de Suporte de TI

## Integrantes

- Pedro Henrique Macedo Cunha
- Guilherme dos Santos Medeiros 

## Problema

Analistas de suporte gastam tempo interpretando chamados incompletos, coletando informações adicionais e classificam manualmente a categoria, prioridade e encaminhamento correto de cada solicitação.

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
`.env.example` lista somente nomes. Provedor padrão: Mistral; modelo `ministral-3b-2512`,
alterável por `LLM_MODEL`. OpenAI é opcional com `LLM_PROVIDER=openai` e `OPENAI_API_KEY`.
Não é necessário recriar `dados/suporte.db`: ele contém fixtures da Parte 1.
Em Linux/macOS, ativação: `source .venv/bin/activate`.

**Validação:** testes locais e recuperação executados. A integração Mistral passou no
teste inicial; os resultados reais dos casos são registrados em `logs/parte2/`.

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
python -m scripts.ablacao
```

Os quatro primeiros não chamam a API. Os dois últimos fazem chamadas pagas e requerem
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
