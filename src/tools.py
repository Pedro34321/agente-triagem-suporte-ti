from database import (
    buscar_equipamento,
    buscar_incidentes_ativos,
    salvar_triagem
)


def consultar_equipamento(patrimonio):
    equipamento = buscar_equipamento(patrimonio)

    if equipamento is None:
        return {
            "sucesso": False,
            "erro": "registro_nao_encontrado",
            "mensagem": f"Equipamento {patrimonio} não encontrado."
        }

    return {
        "sucesso": True,
        "equipamento": equipamento
    }


def consultar_incidentes():
    incidentes = buscar_incidentes_ativos()

    return {
        "sucesso": True,
        "quantidade": len(incidentes),
        "incidentes": incidentes
    }


def consultar_regras():
    return {
        "categorias": [
            "Acesso / Conta",
            "Rede / Conectividade",
            "Software / Sistema",
            "Hardware / Equipamento",
            "Solicitação Informativa"
        ],
        "prioridades": [
            "Baixa",
            "Média",
            "Alta",
            "Crítica"
        ],
        "regras": [
            "Caso crítico deve ser encaminhado para humano.",
            "Registro inexistente nunca deve ser inventado.",
            "Solicitação informativa não deve gerar incidente.",
            "Incidente geral deve prevalecer sobre hipótese individual sem evidência."
        ]
    }


def registrar_triagem(
    relato,
    categoria,
    prioridade,
    encaminhamento,
    justificativa,
    precisa_humano
):
    triagem_id = salvar_triagem(
        relato,
        categoria,
        prioridade,
        encaminhamento,
        justificativa,
        precisa_humano
    )

    return {
        "sucesso": True,
        "triagem_id": triagem_id,
        "mensagem": "Triagem registrada com sucesso."
    }