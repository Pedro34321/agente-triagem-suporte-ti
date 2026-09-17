import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from tools import (
    consultar_equipamento,
    consultar_incidentes,
    consultar_regras,
    registrar_triagem
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

PROMPT_PATH = BASE_DIR / "prompts" / "triagem-v1.txt"

MAX_PASSOS = 5
MAX_TOKENS = 4000
MAX_TEMPO = 60


def carregar_prompt():
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            "Prompt não encontrado em prompts/triagem-v1.txt"
        )

    return PROMPT_PATH.read_text(
        encoding="utf-8"
    )


def criar_cliente():
    base_url = os.getenv("LLM_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada no arquivo .env"
        )

    argumentos = {
        "api_key": api_key
    }

    if base_url:
        argumentos["base_url"] = base_url

    return OpenAI(**argumentos)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_equipamento",
            "description": "Consulta um equipamento pelo patrimônio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patrimonio": {
                        "type": "string"
                    }
                },
                "required": ["patrimonio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_incidentes",
            "description": "Consulta incidentes ativos.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_regras",
            "description": "Consulta as regras de triagem.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_triagem",
            "description": "Registra o resultado final da triagem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relato": {"type": "string"},
                    "categoria": {"type": "string"},
                    "prioridade": {"type": "string"},
                    "encaminhamento": {"type": "string"},
                    "justificativa": {"type": "string"},
                    "precisa_humano": {"type": "boolean"}
                },
                "required": [
                    "relato",
                    "categoria",
                    "prioridade",
                    "encaminhamento",
                    "justificativa",
                    "precisa_humano"
                ]
            }
        }
    }
]


def executar_ferramenta(nome, argumentos):
    try:
        if nome == "consultar_equipamento":
            return consultar_equipamento(**argumentos)

        if nome == "consultar_incidentes":
            return consultar_incidentes()

        if nome == "consultar_regras":
            return consultar_regras()

        if nome == "registrar_triagem":
            return registrar_triagem(**argumentos)

        return {
            "sucesso": False,
            "erro": "ferramenta_desconhecida",
            "mensagem": f"Ferramenta {nome} não existe."
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": "erro_ferramenta",
            "mensagem": str(erro)
        }


def executar_agente(relato):
    cliente = criar_cliente()

    modelo = os.getenv(
        "LLM_MODEL",
        "mistral-small-latest"
    )

    prompt = carregar_prompt()

    mensagens = [
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": relato
        }
    ]

    estado = {
        "objetivo": "realizar triagem",
        "relato": relato,
        "passos": 0,
        "trajetoria": [],
        "motivo_termino": None
    }

    inicio = time.time()

    while estado["passos"] < MAX_PASSOS:

        if time.time() - inicio > MAX_TEMPO:
            estado["motivo_termino"] = "limite_tempo"
            break

        estado["passos"] += 1

        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=mensagens,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1000
        )

        mensagem = resposta.choices[0].message

        if mensagem.tool_calls:

            mensagens.append(mensagem)

            for chamada in mensagem.tool_calls:

                nome = chamada.function.name

                try:
                    argumentos = json.loads(
                        chamada.function.arguments
                    )
                except json.JSONDecodeError:
                    argumentos = {}

                resultado = executar_ferramenta(
                    nome,
                    argumentos
                )

                estado["trajetoria"].append({
                    "passo": estado["passos"],
                    "ferramenta": nome,
                    "argumentos": argumentos,
                    "resultado": resultado
                })

                mensagens.append({
                    "role": "tool",
                    "tool_call_id": chamada.id,
                    "content": json.dumps(
                        resultado,
                        ensure_ascii=False
                    )
                })

            continue

        estado["motivo_termino"] = "resposta_final"

        return {
            "resposta": mensagem.content,
            "estado": estado
        }

    if estado["motivo_termino"] is None:
        estado["motivo_termino"] = "limite_passos"

    return {
        "resposta": (
            "Não foi possível concluir a triagem "
            "automaticamente. Encaminhar para humano."
        ),
        "estado": estado
    }


def main():
    print("=" * 60)
    print("AGENTE DE TRIAGEM DE SUPORTE DE TI")
    print("=" * 60)

    relato = input(
        "\nDescreva o problema: "
    ).strip()

    if not relato:
        print("Nenhum relato informado.")
        return

    resultado = executar_agente(relato)

    print("\n--- RESULTADO ---")
    print(resultado["resposta"])

    print("\n--- TERMINAÇÃO ---")
    print(
        resultado["estado"]["motivo_termino"]
    )

    print("\n--- PASSOS ---")
    print(
        resultado["estado"]["passos"]
    )


if __name__ == "__main__":
    main()