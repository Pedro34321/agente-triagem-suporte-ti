"""Controles locais fora do prompt. Não substitui autenticação empresarial."""
import hmac
import json
import os
import re
import secrets
import hashlib
from pathlib import Path
from .common import canonical, sanitize


HOSTILE = re.compile(r'(?i)(ignore (as|todas as) regras|ignore aprova[çc][ãa]o|revele sua chave|regra permanente|execute powershell|apague o banco)')


class LocalAuthority:
    def __init__(self, directory):
        self.path=Path(directory)/'reviewer.json'
        if not self.path.exists():
            with self.path.open('x',encoding='utf-8') as f:
                json.dump({'principal':'revisor-local','token':secrets.token_urlsafe(32)},f)
            try: self.path.chmod(0o600)
            except OSError: pass
        config=json.loads(self.path.read_text(encoding='utf-8'))
        self._token=config['token']
        self.principal=config['principal']

    def local_credential(self):
        """CLI local usa o segredo do operador com acesso ao arquivo, sem imprimi-lo."""
        return self._token

    def authenticate(self, token, actor):
        if actor!=self.principal or not isinstance(token,str) or not hmac.compare_digest(token,self._token):
            raise PermissionError('Revisor não autorizado.')

    def sign(self, thread, decision, deadline):
        return hmac.new(self._token.encode(),canonical([thread,decision,deadline]).encode(),hashlib.sha256).hexdigest()

    def verify(self, state, now):
        expected=self.sign(state['thread_id'],state['decision'],state.get('deadline',0))
        if now>state.get('deadline',0) or not hmac.compare_digest(state.get('approval_grant',''),expected):
            raise PermissionError('Registro sem aprovação válida bloqueado.')


def suspended():
    if os.getenv('TRIAGEM_SUSPENDED')=='1': raise PermissionError('Agente suspenso pelo operador.')


def validate_episode(payload):
    from pydantic import TypeAdapter
    from .contracts import Category, Priority, Team
    allowed={'assunto','categoria','prioridade','encaminhamento'}
    if not payload or set(payload)-allowed: raise PermissionError('Conteúdo externo não pode virar memória episódica.')
    adapters={'categoria':Category,'prioridade':Priority,'encaminhamento':Team}
    for k,v in payload.items():
        if k in adapters: TypeAdapter(adapters[k]).validate_python(v)
        elif v not in ('acesso','rede','hardware','software','vpn','prioridade','outros'):
            raise PermissionError('Assunto de memória inválido.')


def validate_fact(name,value):
    if not re.fullmatch(r'equipamento:(NB|DT)-\d{5}',name): raise PermissionError('Fato sem fonte de cadastro permitida.')
    if set(value)!={'patrimonio','tipo','status','localizacao'}: raise PermissionError('Fato fora do contrato.')
    if value['patrimonio']!=name.split(':',1)[1] or value['tipo'] not in ('Notebook','Desktop') or value['status'] not in ('Ativo','Manutenção','Inativo'):
        raise PermissionError('Fato não verificado.')
    if not re.fullmatch(r'Andar \d{1,2}|Empresa',value['localizacao']): raise PermissionError('Local de cadastro não permitido.')
