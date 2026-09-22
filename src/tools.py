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
            "Um incidente geral só deve ser relacionado ao chamado quando houver evidência concreta de correspondência, como mesmo serviço afetado, mesma localização ou contexto claramente compatível."
            "Não associe um incidente ao usuário apenas porque existe um incidente ativo no sistema.",
            "Problemas explícitos de senha, autenticação ou credencial devem ser classificados inicialmente como Acesso / Conta, salvo quando houver evidência concreta de outra causa."
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