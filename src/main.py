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
    registrar_triagem,
)


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "triagem-v1.txt"

# Orçamento do agente
MAX_PASSOS = 5
MAX_TOKENS = 4000
MAX_TEMPO = 60


def carregar_prompt():
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            "Prompt não encontrado em prompts/triagem-v1.txt"
        )

    return PROMPT_PATH.read_text(encoding="utf-8")


def criar_cliente():
    base_url = os.getenv("LLM_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada no arquivo .env"
        )

    argumentos = {
        "api_key": api_key,
    }

    if base_url:
        argumentos["base_url"] = base_url

    return OpenAI(**argumentos)


# Ferramentas disponíveis para o modelo
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_equipamento",
            "description": (
                "Consulta informações de um equipamento pelo número de "
                "patrimônio informado explicitamente pelo usuário. "
                "Use somente quando houver um patrimônio no relato ou "
                "quando essa informação for realmente necessária."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "patrimonio": {
                        "type": "string",
                        "description": (
                            "Número de patrimônio informado pelo usuário, "
                            "por exemplo NB-10203."
                        ),
                    }
                },
                "required": ["patrimonio"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_incidentes",
            "description": (
                "Consulta incidentes ativos SOMENTE quando o relato indicar "
                "possível indisponibilidade geral, falha de rede, sistema "
                "indisponível, múltiplos usuários afetados ou impacto coletivo. "
                "NÃO use esta ferramenta para problemas individuais explícitos "
                "de senha, credencial, autenticação ou acesso."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_regras",
            "description": (
                "Consulta as categorias, prioridades e regras oficiais de "
                "triagem. Use para validar a classificação antes da conclusão."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_triagem",
            "description": (
                "Registra o resultado final da triagem no banco de dados. "
                "Use somente quando houver informação suficiente para produzir "
                "uma classificação final."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "relato": {
                        "type": "string",
                    },
                    "categoria": {
                        "type": "string",
                    },
                    "prioridade": {
                        "type": "string",
                    },
                    "encaminhamento": {
                        "type": "string",
                    },
                    "justificativa": {
                        "type": "string",
                    },
                    "precisa_humano": {
                        "type": "boolean",
                    },
                },
                "required": [
                    "relato",
                    "categoria",
                    "prioridade",
                    "encaminhamento",
                    "justificativa",
                    "precisa_humano",
                ],
            },
        },
    },
]


def executar_ferramenta(nome, argumentos):
    """
    Executa uma ferramenta solicitada pelo modelo.

    Erros de ferramenta são retornados como dados para o agente,
    em vez de derrubar o programa.
    """

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
            "mensagem": f"Ferramenta {nome} não existe.",
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": "erro_ferramenta",
            "mensagem": str(erro),
        }


def executar_agente(relato):
    cliente = criar_cliente()

    modelo = os.getenv(
        "LLM_MODEL",
        "ministral-3b-2512",
    )

    prompt = carregar_prompt()

    mensagens = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": relato,
        },
    ]

    estado = {
        "objetivo": "realizar triagem inicial de suporte",
        "relato": relato,
        "passos": 0,
        "tokens_utilizados": 0,
        "trajetoria": [],
        "motivo_termino": None,
    }

    inicio = time.time()

    while estado["passos"] < MAX_PASSOS:

        # Limite de tempo
        if time.time() - inicio > MAX_TEMPO:
            estado["motivo_termino"] = "limite_tempo"
            break

        # Limite de tokens
        if estado["tokens_utilizados"] >= MAX_TOKENS:
            estado["motivo_termino"] = "limite_tokens"
            break

        estado["passos"] += 1

        try:
            resposta = cliente.chat.completions.create(
                model=modelo,
                messages=mensagens,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=1000,
                temperature=0.2,
            )

        except Exception as erro:
            estado["motivo_termino"] = "erro_modelo"

            return {
                "resposta": (
                    "Não foi possível consultar o modelo. "
                    "O caso deve ser encaminhado para análise humana."
                ),
                "estado": estado,
                "erro": str(erro),
            }

        # Registra tokens utilizados quando o provedor fornece usage
        if resposta.usage:
            total_tokens = getattr(
                resposta.usage,
                "total_tokens",
                0,
            )

            estado["tokens_utilizados"] += total_tokens or 0

        mensagem = resposta.choices[0].message

        # O modelo decidiu utilizar uma ou mais ferramentas
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
                    argumentos,
                )

                estado["trajetoria"].append(
                    {
                        "passo": estado["passos"],
                        "ferramenta": nome,
                        "argumentos": argumentos,
                        "resultado": resultado,
                    }
                )

                mensagens.append(
                    {
                        "role": "tool",
                        "tool_call_id": chamada.id,
                        "content": json.dumps(
                            resultado,
                            ensure_ascii=False,
                        ),
                    }
                )

            continue

        # Se não chamou ferramenta, chegou à resposta final
        estado["motivo_termino"] = "resposta_final"

        return {
            "resposta": mensagem.content,
            "estado": estado,
        }

    # Se saiu do laço sem resposta final
    if estado["motivo_termino"] is None:
        estado["motivo_termino"] = "limite_passos"

    return {
        "resposta": (
            "Não foi possível concluir a triagem automaticamente. "
            "O caso deve ser encaminhado para análise humana."
        ),
        "estado": estado,
    }


def main():
    print("=" * 60)
    print("AGENTE DE TRIAGEM DE SUPORTE DE TI")
    print("=" * 60)

    relato = input(
        "\nDescreva o problema: "
    ).strip()

    if not relato:
        print("\nNenhum relato informado.")
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

    print("\n--- TOKENS UTILIZADOS ---")
    print(
        resultado["estado"]["tokens_utilizados"]
    )

    print("\n--- TRAJETÓRIA DAS FERRAMENTAS ---")

    trajetoria = resultado["estado"]["trajetoria"]

    if not trajetoria:
        print("Nenhuma ferramenta foi utilizada.")

    else:
        for item in trajetoria:
            print(
                json.dumps(
                    item,
                    ensure_ascii=False,
                    indent=2,
                )
            )

    if "erro" in resultado:
        print("\n--- ERRO ---")
        print(resultado["erro"])


if __name__ == "__main__":
    main()