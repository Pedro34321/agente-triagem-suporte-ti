from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Category = Literal['Acesso / Conta', 'Rede / Conectividade', 'Software / Sistema',
                   'Hardware / Equipamento', 'Solicitação Informativa']
Priority = Literal['Baixa', 'Média', 'Alta', 'Crítica']
Team = Literal['Suporte N1', 'Infraestrutura', 'Sistemas', 'Suporte N2']


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Interpretation(Strict):
    intent: Literal['falha', 'informacao', 'incompleto', 'ambiguo', 'fora_escopo']
    topic: Literal['acesso', 'rede', 'hardware', 'software', 'vpn', 'prioridade', 'outros']
    query: str = Field(max_length=300)
    asset: str | None
    location: str | None
    collective: bool
    questions: list[str]


class Citation(Strict):
    id: str
    trecho: str = Field(min_length=1)


class Decision(Strict):
    resultado: str = Field(min_length=1, max_length=1800)
    fontes: list[Citation]
    suficiente: bool
    categoria: Category | None
    prioridade: Priority | None
    encaminhamento: Team | None
    perguntas: list[str]
    registrar: bool


class Approval(Strict):
    decisao: Literal['aprovar', 'rejeitar', 'editar']
    prioridade: Priority | None = None
    encaminhamento: Team | None = None


class Output(Decision):
    motivo_termino: str
    thread_id: str
    registro_id: int | None = None
    ja_existia: bool = False
    pendencia: dict | None = None

    @model_validator(mode='after')
    def require_sources(self):
        if self.suficiente and not self.fontes:
            raise ValueError('Uma decisão suficiente exige fonte verificável.')
        if self.registro_id is not None and not self.suficiente:
            raise ValueError('Registro exige decisão suficiente.')
        return self
