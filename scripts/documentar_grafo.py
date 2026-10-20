"""Acrescenta inventário e tabela do estado a partir do grafo e tipo reais."""
import inspect
import re
from src.common import ROOT
from src.graph import State, App
from conferir_grafo import inventory

WRITERS = {
 'owner':'entrada', 'thread_id':'entrada', 'text':'entrada', 'history':'entrada',
 'started':'entrada', 'deadline':'validar', 'interpretation':'interpretar',
 'sources':'recuperar', 'tool_errors':'recuperar', 'memories':'recuperar', 'semantic':'recuperar',
 'decision':'interpretar/responder/validar/aprovar', 'validation':'validar',
 'attempts':'responder', 'calls':'interpretar/responder', 'tokens':'interpretar/responder',
 'signatures':'validar', 'events':'entrada e nós', 'route':'nós de decisão',
 'reason':'interpretar/responder/validar/aprovar/registrar', 'receipt':'registrar', 'output':'finalizar'}
READERS = {
 'owner':'recuperar, registrar, log', 'thread_id':'registrar, finalizar, retomar', 'text':'interpretar, recuperar, responder',
 'history':'interpretar, responder', 'started':'call, registrar', 'deadline':'aprovar, expire',
 'interpretation':'recuperar, responder, validar, registrar', 'sources':'responder, validar, registrar',
 'tool_errors':'responder, validar', 'memories':'responder', 'semantic':'responder',
 'decision':'validar, aprovar, registrar, finalizar', 'validation':'responder', 'attempts':'responder, validar',
 'calls':'call', 'tokens':'call, log', 'signatures':'validar', 'events':'log e scripts de evidência',
 'route':'arestas condicionais', 'reason':'finalizar', 'receipt':'finalizar, run', 'output':'snapshot_output, resume'}


def main():
    path = ROOT / 'docs/arquitetura.md'
    intro = path.read_text(encoding='utf-8').split('<!-- GERADO -->')[0]
    lines = ['<!-- GERADO -->', '', '## Conferência executada', '', '`python conferir_grafo.py`', '', '```text', inventory(), '```', '',
             '## Campos do estado', '', '| Campo | Tipo | Escreve | Lê | Origem |', '|---|---|---|---|---|']
    for field, annotation in State.__annotations__.items():
        type_name = re.sub(r' at 0x[0-9A-Fa-f]+', '', str(annotation)).replace('typing.', '').replace('|', '/')
        origin = 'metadados e texto da CLI' if field in ('owner', 'thread_id', 'text', 'history') else 'nó produtor em src/graph.py'
        lines.append(f'| {field} | `{type_name}` | {WRITERS[field]} | {READERS[field]} | {origin} |')
    lines += ['', 'Escritas múltiplas são sequenciais: não há ramos paralelos no agente.',
              '`events` e `signatures` usam concatenação; `history` concatena e mantém quatro mensagens.',
              'Demais campos substituem o valor anterior. Sem reducer, eventos sequenciais se perdem.',
              'A demonstração paralela da versão instalada levanta InvalidUpdateError, contrariando a hipótese de perda silenciosa do enunciado.', '',
              '## O que o framework não forneceu', '', '| Responsabilidade | Método | Linhas físicas |', '|---|---|---|']
    for name in ('call', 'validar', 'aprovar', 'resume'):
        source, line = inspect.getsourcelines(getattr(App, name))
        lines.append(f'| {name} | src/graph.py:{line} | {len(source)} |')
    lines += ['', 'Contagem inclui assinaturas e comentários; esses métodos também fazem outras tarefas.',
              'Motivo de término é campo próprio; detector compara hashes de decisões inválidas, sem aguardar recursion_limit.',
              'Tetos explícitos: 90s de tempo ativo, 3 chamadas ao modelo, 12000 tokens contabilizados e 16 superpassos.',
              'Tokens são teto observado após chamada, com saída limitada a 1200; não é um limite de cobrança estrito.',
              'Timeout por chamada <=30s e retries=0; tempo de espera humana não conta como execução ativa.',
              'Registro inexistente é recuperável e volta ao modelo como dado; API indisponível termina com erro_modelo.',
              'Falhas inesperadas de armazenamento são fatais e podem exigir diagnóstico; não há repetição automática de escritas.', '',
              'Decisão convertida em parâmetro: recursion_limit=16 e retries=0 são fixados explicitamente.',
              'Alterar padrão de biblioteca não aumenta silenciosamente o orçamento. Versões estão fixadas em requirements.txt.', '',
              '## Padrões e bifurcações', '',
              '| Padrão | Onde | Justificativa / quando não usar |', '|---|---|---|',
              '| Sequencial com portão | responder -> validar | impede ação com fonte inválida; não se aplica à entrada já recusada |',
              '| Router | interpretar -> recuperar/finalizar | texto livre exige modelo; código aplica o enum da rota |',
              '| Avaliador-otimizador | validar -> responder, uma vez | erro verificável pode ser corrigido; repetição encerra |',
              '| Paralelização, orquestrador e agente livre | não usados | tarefas curtas com dependências e ação bem definida |', '',
              'Toda aresta condicional é aplicada por código. Só intenção e suficiência são propostas pelo modelo com schema;',
              'o portão verifica fontes e invariantes. Aprovação vem da pessoa e expiração do relógio.', '',
              '## Fora do estado', '',
              'Histórico guarda texto conversacional; decisões e contadores têm campos próprios.',
              'Não se guardam cliente OpenAI, conexão SQLite, API key, índice do corpus nem custo monetário estimado.',
              'Hash de idempotência, score lexical e duração são derivados. Há um único agente; nenhum contrato entre agentes.', '',
              'Términos: incompleto, ambiguo, fora_escopo, informativo, base_insuficiente, registrado, rejeitado,',
              'aprovacao_expirada, laco_detectado, validacao_falhou, erro_modelo, limite_tempo, limite_chamadas,',
              'limite_tokens e limite_orcamento. aguardando_aprovacao é suspensão, não conclusão.', '']
    path.write_text(intro + '\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
