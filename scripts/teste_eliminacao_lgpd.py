import json
import shutil
import sqlite3
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_ORIGINAL = BASE_DIR / "dados" / "suporte.db"

# Titular 100% fictício criado somente para o teste de eliminação.
TITULAR = "TITULAR_TESTE_LGPD_001"
PATRIMONIO = "NB-LGPD-001"


def consultar_dados(conexao):
    """
    Procura o titular de teste em todas as tabelas do banco
    em que inserimos seus dados.
    """
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT patrimonio, usuario, tipo, status, localizacao
        FROM equipamentos
        WHERE usuario = ? OR patrimonio = ?
        """,
        (TITULAR, PATRIMONIO),
    )

    equipamentos = [dict(linha) for linha in cursor.fetchall()]

    cursor.execute(
        """
        SELECT
            id,
            relato,
            categoria,
            prioridade,
            encaminhamento,
            justificativa,
            precisa_humano
        FROM triagens
        WHERE relato LIKE ?
           OR justificativa LIKE ?
        """,
        (f"%{TITULAR}%", f"%{TITULAR}%"),
    )

    triagens = [dict(linha) for linha in cursor.fetchall()]

    return {
        "equipamentos": equipamentos,
        "triagens": triagens,
    }


def imprimir_estado(titulo, dados):
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)
    print(
        json.dumps(
            dados,
            ensure_ascii=False,
            indent=2,
        )
    )


def main():
    print("=" * 70)
    print("TESTE DE ELIMINAÇÃO DE DADOS — LGPD")
    print("=" * 70)

    print()
    print(f"Titular fictício: {TITULAR}")
    print(f"Patrimônio fictício: {PATRIMONIO}")

    if not DB_ORIGINAL.exists():
        raise FileNotFoundError(
            f"Banco não encontrado em: {DB_ORIGINAL}"
        )

    print()
    print(f"Banco de referência: {DB_ORIGINAL}")
    print(
        "O banco original NÃO será alterado. "
        "O teste será executado em uma cópia temporária."
    )

    with tempfile.TemporaryDirectory(
        prefix="agente_lgpd_"
    ) as pasta_temporaria:

        db_teste = (
            Path(pasta_temporaria)
            / "suporte_teste_lgpd.db"
        )

        shutil.copy2(
            DB_ORIGINAL,
            db_teste,
        )

        # ---------------------------------------------------------
        # PREPARAÇÃO DOS DADOS DO TITULAR FICTÍCIO
        # ---------------------------------------------------------

        conexao = sqlite3.connect(db_teste)
        cursor = conexao.cursor()

        # Remove qualquer vestígio anterior somente na cópia.
        cursor.execute(
            """
            DELETE FROM triagens
            WHERE relato LIKE ?
               OR justificativa LIKE ?
            """,
            (f"%{TITULAR}%", f"%{TITULAR}%"),
        )

        cursor.execute(
            """
            DELETE FROM equipamentos
            WHERE usuario = ?
               OR patrimonio = ?
            """,
            (TITULAR, PATRIMONIO),
        )

        # Insere dado pessoal fictício na tabela equipamentos.
        cursor.execute(
            """
            INSERT INTO equipamentos (
                patrimonio,
                usuario,
                tipo,
                status,
                localizacao
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                PATRIMONIO,
                TITULAR,
                "Notebook",
                "Ativo",
                "Andar de Teste LGPD",
            ),
        )

        # Insere uma triagem associada ao titular fictício.
        cursor.execute(
            """
            INSERT INTO triagens (
                relato,
                categoria,
                prioridade,
                encaminhamento,
                justificativa,
                precisa_humano
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                (
                    f"{TITULAR}: meu notebook de teste "
                    "não está conectando à rede."
                ),
                "Rede / Conectividade",
                "Média",
                "Suporte N1",
                (
                    "Triagem fictícia criada exclusivamente "
                    f"para o teste LGPD do {TITULAR}."
                ),
                0,
            ),
        )

        conexao.commit()

        # ---------------------------------------------------------
        # ANTES DA ELIMINAÇÃO
        # ---------------------------------------------------------

        antes = consultar_dados(conexao)

        imprimir_estado(
            "ANTES DA ELIMINAÇÃO",
            antes,
        )

        print()
        print(
            "Quantidade encontrada em equipamentos:",
            len(antes["equipamentos"]),
        )
        print(
            "Quantidade encontrada em triagens:",
            len(antes["triagens"]),
        )

        # ---------------------------------------------------------
        # PEDIDO DE ELIMINAÇÃO
        # ---------------------------------------------------------

        print()
        print("=" * 70)
        print("EXECUTANDO PEDIDO DE ELIMINAÇÃO")
        print("=" * 70)

        cursor = conexao.cursor()

        cursor.execute(
            """
            DELETE FROM triagens
            WHERE relato LIKE ?
               OR justificativa LIKE ?
            """,
            (f"%{TITULAR}%", f"%{TITULAR}%"),
        )

        triagens_removidas = cursor.rowcount

        cursor.execute(
            """
            DELETE FROM equipamentos
            WHERE usuario = ?
               OR patrimonio = ?
            """,
            (TITULAR, PATRIMONIO),
        )

        equipamentos_removidos = cursor.rowcount

        conexao.commit()
        conexao.close()

        print(
            f"Triagens removidas: {triagens_removidas}"
        )
        print(
            "Equipamentos associados removidos:",
            equipamentos_removidos,
        )

        # ---------------------------------------------------------
        # VERIFICAÇÃO INDEPENDENTE
        #
        # Abre uma NOVA conexão depois da remoção.
        # Assim, a verificação não depende da conexão que executou
        # os DELETEs.
        # ---------------------------------------------------------

        conexao_verificacao = sqlite3.connect(
            db_teste
        )

        depois = consultar_dados(
            conexao_verificacao
        )

        conexao_verificacao.close()

        imprimir_estado(
            "DEPOIS DA ELIMINAÇÃO",
            depois,
        )

        print()
        print(
            "Quantidade encontrada em equipamentos:",
            len(depois["equipamentos"]),
        )
        print(
            "Quantidade encontrada em triagens:",
            len(depois["triagens"]),
        )

        # ---------------------------------------------------------
        # RESULTADO
        # ---------------------------------------------------------

        eliminado = (
            len(depois["equipamentos"]) == 0
            and len(depois["triagens"]) == 0
        )

        print()
        print("=" * 70)
        print("VERIFICAÇÃO FINAL")
        print("=" * 70)

        if eliminado:
            print(
                "RESULTADO: APROVADO — "
                "o titular fictício não foi encontrado "
                "nas estruturas verificadas."
            )
        else:
            print(
                "RESULTADO: FALHOU — "
                "ainda existem dados associados ao titular."
            )

        print()
        print("Estruturas verificadas:")
        print("- tabela equipamentos")
        print("- tabela triagens")

        print()
        print("Estruturas não utilizadas neste teste:")
        print("- índice vetorial: não utilizado")
        print("- memória persistente: não implementada")
        print("- provedor LLM: não acionado")
        print("- logs do agente: não gravados por este teste")
        print("- prompt: nenhum dado do titular foi inserido")

        print()
        print(
            "Observação: a saída desta execução pode ser "
            "preservada como evidência porque o titular "
            "utilizado é totalmente fictício."
        )


if __name__ == "__main__":
    main()