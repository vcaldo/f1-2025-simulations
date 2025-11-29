"""
Módulo de conexão com banco de dados DuckDB.

Gerencia conexão, criação de tabelas e verificação de estado.
"""

import duckdb
from pathlib import Path

# Caminho do banco de dados
DATA_DIR = Path(__file__).parent.parent / 'data'
DB_PATH = DATA_DIR / 'f1_simulations.duckdb'


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Retorna conexão com o banco de dados DuckDB.

    Cria o diretório data/ se não existir.

    Returns:
        Conexão DuckDB persistente.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def table_exists(conn: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    """
    Verifica se uma tabela existe no banco.

    Args:
        conn: Conexão DuckDB
        table_name: Nome da tabela

    Returns:
        True se a tabela existe, False caso contrário.
    """
    result = conn.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
        [table_name]
    ).fetchone()
    return result[0] > 0


def table_count(conn: duckdb.DuckDBPyConnection, table_name: str) -> int:
    """
    Retorna o número de registros em uma tabela.

    Args:
        conn: Conexão DuckDB
        table_name: Nome da tabela

    Returns:
        Número de registros na tabela.
    """
    if not table_exists(conn, table_name):
        return 0
    result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    return result[0]


def is_populated(conn: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    """
    Verifica se uma tabela existe e contém dados.

    Args:
        conn: Conexão DuckDB
        table_name: Nome da tabela

    Returns:
        True se a tabela existe e tem registros, False caso contrário.
    """
    return table_exists(conn, table_name) and table_count(conn, table_name) > 0


def create_cenarios_empate_table(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Cria a tabela cenarios_empate se não existir.

    Args:
        conn: Conexão DuckDB
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cenarios_empate (
            sprint_norris INTEGER,
            sprint_piastri INTEGER,
            sprint_verstappen INTEGER,
            corrida_norris INTEGER,
            corrida_piastri INTEGER,
            corrida_verstappen INTEGER,
            pts_norris INTEGER,
            pts_piastri INTEGER,
            pts_verstappen INTEGER,
            ganhos_norris INTEGER,
            ganhos_piastri INTEGER,
            ganhos_verstappen INTEGER,
            pontos_empate INTEGER,
            tipo_empate VARCHAR,
            pilotos_empatados VARCHAR
        )
    """)
