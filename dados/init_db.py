import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "suporte.db"


def criar_banco():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            patrimonio TEXT PRIMARY KEY,
            usuario TEXT NOT NULL,
            tipo TEXT NOT NULL,
            status TEXT NOT NULL,
            localizacao TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            localizacao TEXT,
            usuarios_afetados INTEGER,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS triagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relato TEXT NOT NULL,
            categoria TEXT,
            prioridade TEXT,
            encaminhamento TEXT,
            justificativa TEXT,
            precisa_humano INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("DELETE FROM equipamentos")
    cursor.execute("DELETE FROM incidentes")

    equipamentos = [
        (
            "NB-10203",
            "João Silva",
            "Notebook",
            "Ativo",
            "Andar 3"
        ),
        (
            "NB-20510",
            "Maria Souza",
            "Notebook",
            "Ativo",
            "Andar 2"
        ),
        (
            "DT-30021",
            "Carlos Santos",
            "Desktop",
            "Ativo",
            "Andar 1"
        )
    ]

    cursor.executemany("""
        INSERT INTO equipamentos
        (patrimonio, usuario, tipo, status, localizacao)
        VALUES (?, ?, ?, ?, ?)
    """, equipamentos)

    incidentes = [
        (
            "Indisponibilidade de rede no andar 3",
            "Rede / Conectividade",
            "Andar 3",
            35,
            "Ativo"
        ),
        (
            "Instabilidade temporária do sistema de vendas",
            "Software / Sistema",
            "Empresa",
            18,
            "Resolvido"
        )
    ]

    cursor.executemany("""
        INSERT INTO incidentes
        (titulo, categoria, localizacao, usuarios_afetados, status)
        VALUES (?, ?, ?, ?, ?)
    """, incidentes)

    conexao.commit()
    conexao.close()

    print(f"Banco criado com sucesso em: {DB_PATH}")


if __name__ == "__main__":
    criar_banco()