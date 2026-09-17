import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "dados" / "suporte.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def buscar_equipamento(patrimonio):
    conexao = conectar()
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM equipamentos WHERE patrimonio = ?",
        (patrimonio,)
    )

    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return None

    return dict(resultado)


def buscar_incidentes_ativos():
    conexao = conectar()
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM incidentes WHERE status = 'Ativo'"
    )

    resultados = cursor.fetchall()
    conexao.close()

    return [dict(item) for item in resultados]


def salvar_triagem(
    relato,
    categoria,
    prioridade,
    encaminhamento,
    justificativa,
    precisa_humano
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO triagens (
            relato,
            categoria,
            prioridade,
            encaminhamento,
            justificativa,
            precisa_humano
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        relato,
        categoria,
        prioridade,
        encaminhamento,
        justificativa,
        int(precisa_humano)
    ))

    triagem_id = cursor.lastrowid

    conexao.commit()
    conexao.close()

    return triagem_id