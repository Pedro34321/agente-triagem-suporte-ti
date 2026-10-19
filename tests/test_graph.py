import json
import pytest
from src.graph import App
from src.contracts import Output
from src.knowledge import search


class FakeLLM:
    """Double explícito: valida orquestração, não qualidade do modelo."""
    def __init__(self, invalid=False):
        self.invalid = invalid
    def call(self, name, schema, data, **kwargs):
        if name == 'interpretar':
            return {'intent': 'falha', 'topic': 'acesso', 'query': 'senha email', 'asset': None, 'location': None, 'collective': False, 'questions': []}, 10
        source = next(x for x in data['fontes'] if x['id'] == 'KB-ACESSO')
        return {'resultado': 'Senha rejeitada: encaminhar ao N1.', 'fontes': ['inventada' if self.invalid else source['id']],
                'suficiente': True, 'categoria': 'Acesso / Conta', 'prioridade': 'Média', 'encaminhamento': 'Suporte N1', 'perguntas': [], 'registrar': True}, 20


def count(app):
    with app.store.connect() as db:
        return db.execute('SELECT count(*) FROM triagens').fetchone()[0]


def test_restart_edit_and_duplicate(tmp_path):
    app = App(tmp_path, FakeLLM())
    paused = app.run('senha email rejeitada')
    assert paused['motivo_termino'] == 'aguardando_aprovacao'
    assert count(app) == 0
    app.close()
    app = App(tmp_path, FakeLLM())
    out = app.resume(paused['thread_id'], {'decisao': 'editar', 'encaminhamento': 'Suporte N2'})
    assert out['encaminhamento'] == 'Suporte N2'
    assert out['registro_id'] is not None
    again = app.resume(paused['thread_id'], {'decisao': 'aprovar'})
    assert again['ja_existia'] and count(app) == 1
    snap = app.graph.get_state(app.config(paused['thread_id'])).values
    receipt = app.store.register('demo', paused['thread_id'], snap['decision'])
    assert receipt['ja_existia'] and count(app) == 1
    Output.model_validate(out)
    app.close()


@pytest.mark.parametrize('action', ['rejeitar', 'expirar'])
def test_no_write_on_rejection_or_timeout(tmp_path, action):
    now = [1000.0]
    app = App(tmp_path, FakeLLM(), clock=lambda: now[0])
    out = app.run('senha email rejeitada')
    if action == 'expirar':
        now[0] += 86401
        assert app.expire()[0]['motivo_termino'] == 'aprovacao_expirada'
    else:
        assert app.resume(out['thread_id'], {'decisao': 'rejeitar'})['motivo_termino'] == 'rejeitado'
    assert count(app) == 0
    app.close()


def test_invalid_citation_loop_stops(tmp_path):
    app = App(tmp_path, FakeLLM(invalid=True))
    out = app.run('senha email rejeitada')
    assert out['motivo_termino'] == 'laco_detectado'
    assert not out['suficiente'] and count(app) == 0
    app.close()


def test_revoked_document():
    assert 'KB-VPN-REVOGADO' not in [x['id'] for x in search('configurar VPN', 'vpn')]
    assert 'KB-VPN-REVOGADO' in [x['id'] for x in search('configurar VPN', 'vpn', True)]


def test_forgetting_and_contradiction(tmp_path):
    app = App(tmp_path, FakeLLM())
    user = 'TITULAR_FICTICIO_782'
    out = app.run('senha email rejeitada', user=user)
    app.resume(out['thread_id'], {'decisao': 'aprovar'})
    app.store.fact(user, 'local', 'Andar 1', 1)
    app.store.fact(user, 'local', 'Andar 2', 2)
    assert json.loads(app.store.latest(user, 'local')['atual']['value']) == 'Andar 2'
    assert app.store.recall(user, 'Acesso Conta')
    app.store.forget(user, app.checkpointer)
    assert not app.store.recall(user, 'Acesso Conta')
    assert not app.store.latest(user, 'local')['atual']
    assert not app.graph.get_state(app.config(out['thread_id'])).values
    for table in ('checkpoints', 'writes'):
        # Todas as linhas, não só a consulta do último checkpoint.
        for row in app.conn.execute(f'SELECT * FROM {table}'):
            assert all(user not in str(cell) and (not isinstance(cell, bytes) or user.encode() not in cell) for cell in row)
    with app.store.connect() as db:
        for line in db.iterdump():
            assert user not in line
    for path in (tmp_path / 'logs').glob('*.jsonl'):
        assert user not in path.read_text(encoding='utf-8')
    app.close()


def test_memory_idempotence_decay_and_isolation(tmp_path):
    app = App(tmp_path, FakeLLM())
    payload = {'categoria': 'Acesso / Conta'}
    app.store.remember('u1', payload, created=1)
    assert app.store.remember('u1', payload)['ja_existia']
    assert not app.store.recall('u2', 'Acesso Conta')
    recent = app.store.recall('u1', 'Acesso Conta', now=2)[0]['score']
    old = app.store.recall('u1', 'Acesso Conta', now=100 * 86400)[0]['score']
    assert old < recent
    app.close()


def test_invalid_approval_keeps_pause(tmp_path):
    app = App(tmp_path, FakeLLM())
    out = app.run('senha email rejeitada')
    with pytest.raises(ValueError):
        app.resume(out['thread_id'], {'decisao': 'editar', 'encaminhamento': 'Equipe inventada'})
    assert app.graph.get_state(app.config(out['thread_id'])).next
    assert count(app) == 0
    app.close()


def test_information_never_writes_even_if_model_requests(tmp_path):
    class Informative(FakeLLM):
        def call(self, name, schema, data, **kwargs):
            result, used = super().call(name, schema, data, **kwargs)
            if name == 'interpretar':
                result['intent'] = 'informacao'
            return result, used
    app = App(tmp_path, Informative())
    out = app.run('Como funciona a senha do email?')
    assert out['motivo_termino'] == 'laco_detectado'
    assert count(app) == 0
    app.close()


def test_elapsed_budget_and_provider_failure(tmp_path):
    class Failing:
        def call(self, *args, **kwargs):
            raise RuntimeError('não exportar detalhes internos')
    app = App(tmp_path, Failing(), clock=lambda: 1000)
    out = app.run('senha rejeitada')
    assert out['motivo_termino'] == 'erro_modelo'
    result = app.call({'started': 1}, 'interpretar', None, {})
    assert result['reason'] == 'limite_tempo'
    assert count(app) == 0
    app.close()
