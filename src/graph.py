import json
import operator
import os
import re
import sqlite3
import time
from functools import lru_cache
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command
from .common import ROOT, canonical, digest, sanitize
from .contracts import Interpretation, Decision, Approval, Output
from .knowledge import search, records
from .model import LLM, MODEL, prompt, prompt_versions
from .storage import Store

MAX_SECONDS = 90
MAX_CALLS = 3
MAX_TOKENS = 12000
RECURSION_LIMIT = 16
APPROVAL_SECONDS = 86400


def history_reducer(old, new):
    # Mantém as quatro mensagens recentes; o pedido atual não é descartado.
    return (old + new)[-4:]


class State(TypedDict, total=False):
    owner: str
    thread_id: str
    text: str
    history: Annotated[list[str], history_reducer]
    started: float
    deadline: float
    interpretation: dict
    sources: list[dict]
    tool_errors: list[dict]
    memories: list[dict]
    semantic: dict
    decision: dict
    validation: list[str]
    attempts: int
    calls: int
    tokens: int
    signatures: Annotated[list[str], operator.add]
    events: Annotated[list[dict], operator.add]
    route: str
    reason: str
    receipt: dict
    output: dict


def refusal(message, questions=None):
    return Decision(resultado=message, fontes=[], suficiente=False, categoria=None,
                    prioridade=None, encaminhamento=None, perguntas=questions or [], registrar=False).model_dump()


class App:
    def __init__(self, directory=None, llm=None, clock=time.time):
        self.directory = directory or ROOT / '.runtime'
        self.store = Store(self.directory)
        self.conn = sqlite3.connect(self.directory / 'checkpoints.sqlite', check_same_thread=False)
        self.conn.execute('PRAGMA secure_delete=ON')
        self.checkpointer = SqliteSaver(self.conn)
        self.checkpointer.setup()
        self.llm = llm or LLM()
        self.clock = clock
        builder = StateGraph(State)
        for name in ('interpretar', 'recuperar', 'responder', 'validar', 'aprovar', 'registrar', 'finalizar'):
            builder.add_node(name, getattr(self, name))
        builder.add_edge(START, 'interpretar')
        builder.add_conditional_edges('interpretar', lambda s: s['route'], {'recuperar': 'recuperar', 'finalizar': 'finalizar'})
        builder.add_edge('recuperar', 'responder')
        builder.add_conditional_edges('responder', lambda s: s['route'], {'validar': 'validar', 'finalizar': 'finalizar'})
        builder.add_conditional_edges('validar', lambda s: s['route'], {'responder': 'responder', 'aprovar': 'aprovar', 'finalizar': 'finalizar'})
        builder.add_conditional_edges('aprovar', lambda s: s['route'], {'registrar': 'registrar', 'finalizar': 'finalizar'})
        builder.add_edge('registrar', 'finalizar')
        builder.add_edge('finalizar', END)
        self.graph = builder.compile(checkpointer=self.checkpointer)

    def config(self, thread):
        return {'configurable': {'thread_id': thread}, 'recursion_limit': RECURSION_LIMIT}

    def call(self, state, name, schema, data):
        elapsed = self.clock() - state['started']
        reason = ('limite_tempo' if elapsed >= MAX_SECONDS else
                  'limite_chamadas' if state.get('calls', 0) >= MAX_CALLS else
                  'limite_tokens' if state.get('tokens', 0) >= MAX_TOKENS else '')
        if reason:
            return {'route': 'finalizar', 'reason': reason, 'decision': refusal('Orçamento esgotado; encaminhe ao analista N1.')}
        try:
            result, used = self.llm.call(name, schema, data, timeout=MAX_SECONDS - elapsed)
            updates = {'calls': state.get('calls', 0) + 1, 'tokens': state.get('tokens', 0) + used,
                       'events': [{'node': name, 'tokens': used, 'modelo': MODEL}]}
            if self.clock() - state['started'] >= MAX_SECONDS or updates['tokens'] > MAX_TOKENS:
                updates.update(route='finalizar', reason='limite_orcamento', decision=refusal('Orçamento excedido; nenhuma ação foi autorizada.'))
            else:
                updates['result'] = result
            return updates
        except Exception as exc:
            # Nunca registrar str(exc): mensagens de provedores podem conter dados do pedido.
            body = getattr(exc, 'body', {})
            error = body.get('error', body) if isinstance(body, dict) else {}
            code = error.get('code')
            safe_code = code if code in ('credit_balance_exhausted', 'insufficient_quota', 'rate_limit_exceeded', 'model_not_found', 'invalid_api_key') else None
            return {'route': 'finalizar', 'reason': 'erro_modelo', 'decision': refusal('Modelo indisponível; tente mais tarde ou procure o analista N1.'),
                    'events': [{'node': name, 'erro': type(exc).__name__, 'status': getattr(exc, 'status_code', None), 'codigo': safe_code}]}

    def interpretar(self, state):
        update = self.call(state, 'interpretar', Interpretation, {'relato': state['text'], 'historico': state.get('history', [])[:-1]})
        if 'result' not in update:
            return update
        info = update.pop('result')
        # Identificador nunca é inferido do nada pelo modelo.
        if info['asset'] and info['asset'] not in '\n'.join(state.get('history', [])):
            info['asset'] = None
        update['interpretation'] = info
        if info['intent'] in ('incompleto', 'ambiguo', 'fora_escopo'):
            if info['intent'] != 'fora_escopo' and not info['questions']:
                info['questions'] = ['Qual problema de TI ocorre, em qual sistema e qual mensagem de erro aparece?']
            msg = 'Atendo triagem de suporte de TI. ' if info['intent'] == 'fora_escopo' else 'Preciso de informações adicionais. '
            update.update(route='finalizar', reason=info['intent'], decision=refusal(msg + ' '.join(info['questions']), info['questions']))
        else:
            update['route'] = 'recuperar'
        return update

    def recuperar(self, state):
        info = state['interpretation']
        docs = search(info['query'], info['topic'])
        rows, errors = records(info)
        memories = self.store.recall(state['owner'], state['text'])
        semantic = self.store.latest(state['owner'], 'equipamento:' + (info['asset'] or 'nenhum'))
        return {'sources': docs + rows, 'tool_errors': errors, 'memories': memories, 'semantic': semantic,
                'events': [{'node': 'recuperar', 'chamadas_recuperacao': 1, 'fontes': [s['id'] for s in docs + rows],
                            'erros': errors, 'memorias': memories, 'semantica': semantic}]}

    def responder(self, state):
        if not state['sources']:
            return {'decision': refusal('O corpus de suporte não contém informação para responder a este pedido. Consulte o Suporte N1 para obter o procedimento autorizado.'),
                    'reason': 'base_insuficiente', 'route': 'finalizar'}
        update = self.call(state, 'responder', Decision, {'relato': state['text'], 'historico': state.get('history', []),
                           'interpretacao': state['interpretation'], 'fontes': state['sources'],
                           'erros_ferramentas': state['tool_errors'], 'memorias': state['memories'],
                           'fatos_anteriores': state['semantic'], 'corrigir': state.get('validation', [])})
        if 'result' in update:
            update.update(decision=update.pop('result'), route='validar', attempts=state.get('attempts', 0) + 1)
        return update

    def validar(self, state):
        d = Decision.model_validate(state['decision']).model_dump()
        source_map = {s['id']: s['texto'] for s in state['sources']}
        errors = []
        if d['suficiente'] and not d['fontes']:
            errors.append('Decisão suficiente exige fonte.')
        for cite in d['fontes']:
            if cite['id'] not in source_map or cite['trecho'] not in source_map[cite['id']]:
                errors.append('Citação inválida: use id recuperado e trecho literal.')
        if state['tool_errors'] and (d['suficiente'] or d['registrar']):
            errors.append('Cadastro inexistente: peça confirmação e não registre.')
        if not state['sources'] and d['suficiente']:
            errors.append('Sem corpus suficiente: recuse.')
        if (state['interpretation']['intent'] == 'informacao' or d['categoria'] == 'Solicitação Informativa') and d['registrar']:
            errors.append('Informação não registra incidente.')
        if d['registrar'] and (not d['suficiente'] or not all(d[k] for k in ('categoria', 'prioridade', 'encaminhamento'))):
            errors.append('Registro exige classificação completa e suficiente.')
        if not d['suficiente'] and not d['perguntas'] and state['tool_errors']:
            errors.append('Peça explicitamente confirmação do patrimônio informado.')
        signature = digest(d)
        if errors:
            repeated = signature in state.get('signatures', [])
            if repeated or state['attempts'] >= 2:
                return {'decision': refusal('Não consegui validar a decisão e as fontes. Encaminhe ao analista N1.'),
                        'reason': 'laco_detectado' if repeated else 'validacao_falhou', 'route': 'finalizar', 'validation': errors}
            return {'route': 'responder', 'validation': errors, 'signatures': [signature]}
        if d['registrar']:
            return {'route': 'aprovar', 'deadline': self.clock() + APPROVAL_SECONDS, 'validation': []}
        if not d['suficiente']:
            d.update(categoria=None, prioridade=None, encaminhamento=None, registrar=False)
        return {'decision': d, 'route': 'finalizar', 'reason': 'informativo' if d['suficiente'] else 'base_insuficiente', 'validation': []}

    def aprovar(self, state):
        # Sem efeitos colaterais antes de interrupt: este nó reinicia na retomada.
        if self.clock() > state['deadline']:
            return {'route': 'finalizar', 'reason': 'aprovacao_expirada'}
        response = interrupt({'acao': 'registrar_triagem', 'argumentos': state['decision'],
                              'aviso': prompt('aprovacao'), 'expira_em_unix': state['deadline'],
                              'respostas': ['aprovar', 'rejeitar', 'editar'], 'campos_editaveis': ['prioridade', 'encaminhamento']})
        if self.clock() > state['deadline']:
            return {'route': 'finalizar', 'reason': 'aprovacao_expirada'}
        approval = Approval.model_validate(response)
        if approval.decisao == 'rejeitar':
            return {'route': 'finalizar', 'reason': 'rejeitado'}
        decision = dict(state['decision'])
        if approval.decisao == 'editar':
            for field in ('prioridade', 'encaminhamento'):
                if getattr(approval, field) is not None:
                    decision[field] = getattr(approval, field)
        Decision.model_validate(decision)
        return {'route': 'registrar', 'decision': decision, 'events': [{'node': 'aprovar', 'decisao': approval.model_dump()}]}

    def registrar(self, state):
        receipt = self.store.register(state['owner'], state['thread_id'], state['decision'])
        # Se falhar entre as duas escritas, o replay não duplica nenhuma delas.
        memory = self.store.remember(state['owner'], {'assunto': state['interpretation']['topic'], 'consulta': sanitize(state['interpretation']['query']), 'categoria': state['decision']['categoria'],
                                     'prioridade': state['decision']['prioridade'], 'encaminhamento': state['decision']['encaminhamento']})
        facts = []
        for source in state['sources']:
            if source['id'].startswith('equipamento:'):
                facts.append(self.store.fact(state['owner'], source['id'], json.loads(source['texto']), state['started']))
        return {'receipt': receipt, 'reason': 'registrado', 'events': [{'node': 'registrar', 'recibo': receipt, 'memoria': memory, 'fatos': facts}]}

    def finalizar(self, state):
        receipt = state.get('receipt', {})
        output = Output(**state['decision'], motivo_termino=state['reason'], thread_id=state['thread_id'],
                        registro_id=receipt.get('registro_id'), ja_existia=receipt.get('ja_existia', False)).model_dump()
        return {'output': output, 'events': [{'node': 'finalizar', 'motivo': state['reason']}]}

    def snapshot_output(self, state):
        if state.get('__interrupt__'):
            return Output(**state['decision'], motivo_termino='aguardando_aprovacao', thread_id=state['thread_id'],
                          pendencia=state['__interrupt__'][0].value).model_dump()
        return state['output']

    def log(self, owner, thread, operation, output, state):
        directory = self.directory / 'logs'
        directory.mkdir(exist_ok=True)
        entry = {'owner': owner, 'thread': thread, 'operacao': operation, 'data_unix': self.clock(),
                 'modelo': MODEL, 'prompts': prompt_versions(), 'output': output,
                 'tokens': state.get('tokens', 0), 'events': state.get('events', [])}
        with (directory / (digest(thread) + '.jsonl')).open('a', encoding='utf-8') as f:
            f.write(canonical(entry) + '\n')

    def run(self, text, user='demo', session='principal', case='caso1'):
        if not isinstance(text, str) or not text.strip() or len(text) > 2000:
            raise ValueError('Informe texto livre com 1 a 2000 caracteres.')
        if any(not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', x) for x in (user, session, case)):
            raise ValueError('Identificadores devem usar letras, números, _ ou - (até 64).')
        thread = f'{user}:{session}:{case}'
        cfg = self.config(thread)
        previous = self.graph.get_state(cfg)
        if previous.next:
            raise ValueError('Existe aprovação pendente. Use retomar ou rejeite a proposta.')
        if previous.values.get('receipt'):
            raise ValueError('Caso já registrado. Use um novo --caso.')
        self.store.track(thread, user)
        initial = {'owner': user, 'thread_id': thread, 'text': sanitize(text), 'history': [sanitize(text)],
                   'started': self.clock(), 'calls': 0, 'tokens': 0, 'attempts': 0, 'validation': [], 'receipt': {},
                   'sources': [], 'tool_errors': [], 'memories': [], 'semantic': {}, 'reason': '',
                   'events': [{'node': 'inicio', 'modelo': MODEL, 'prompts': prompt_versions(), 'data_unix': self.clock()}]}
        state = self.graph.invoke(initial, cfg)
        output = self.snapshot_output(state)
        self.log(user, thread, 'iniciar', output, state)
        return output

    def resume(self, thread, response):
        approval = Approval.model_validate(response)
        cfg = self.config(thread)
        snap = self.graph.get_state(cfg)
        if not snap.values:
            raise ValueError('Conversa inexistente.')
        if not snap.next:
            output = dict(snap.values['output'])
            output['ja_existia'] = output['registro_id'] is not None
            self.log(snap.values['owner'], thread, 'retomada_repetida', output, snap.values)
            return output
        state = self.graph.invoke(Command(resume=approval.model_dump()), cfg)
        output = self.snapshot_output(state)
        self.log(state['owner'], thread, 'retomar', output, state)
        return output

    def expire(self):
        expired = []
        with self.store.connect() as db:
            threads = [r['thread'] for r in db.execute('SELECT thread FROM threads')]
        for thread in threads:
            snap = self.graph.get_state(self.config(thread))
            if snap.next and snap.values.get('deadline', float('inf')) < self.clock():
                expired.append(self.resume(thread, {'decisao': 'rejeitar'}))
        return expired

    def close(self):
        self.conn.close()


@lru_cache(maxsize=1)
def get_app():
    from pathlib import Path
    return App(Path(os.environ['TRIAGEM_RUNTIME']) if os.getenv('TRIAGEM_RUNTIME') else None)
