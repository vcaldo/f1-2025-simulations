"""
Módulo de banco de dados para simulações F1 2025.
"""

from .connection import (
    get_connection,
    table_exists,
    table_count,
    is_populated,
    create_cenarios_empate_table,
    DB_PATH,
    DATA_DIR
)

__all__ = [
    'get_connection',
    'table_exists',
    'table_count',
    'is_populated',
    'create_cenarios_empate_table',
    'DB_PATH',
    'DATA_DIR'
]
