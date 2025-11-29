"""
Simulador de Cenários de Empate - Qatar (Penúltima Etapa)

Gera todas as combinações de resultados (sprint + corrida) onde 2 ou 3 pilotos
terminam empatados em pontos antes da última corrida regular.

Posições fora dos pontos representadas como 99.
"""

import csv
from itertools import product
from pathlib import Path

from config.settings import (
    PONTOS_SPRINT, PONTOS_CORRIDA,
    POSICOES_SPRINT, POSICOES_CORRIDA,
    PILOTOS_SIMULADOR
)
from database import (
    get_connection,
    is_populated,
    create_cenarios_empate_table
)

# Caminho padrão para exportar CSV (mantido para backup)
DATA_DIR = Path(__file__).parent / 'data'
CSV_PATH = DATA_DIR / 'cenarios_empate.csv'


def posicoes_validas(pos1: int, pos2: int, pos3: int) -> bool:
    """
    Verifica se a combinação de posições é válida.
    Dois pilotos não podem ocupar a mesma posição pontuada.
    Posição 99 (fora dos pontos) pode ser compartilhada.
    """
    posicoes = [pos1, pos2, pos3]
    posicoes_pontuadas = [p for p in posicoes if p != 99]
    return len(posicoes_pontuadas) == len(set(posicoes_pontuadas))


def calcular_pontos(pontos_atuais: int, pos_sprint: int, pos_corrida: int) -> int:
    """Calcula pontos finais somando pontos da sprint e corrida aos atuais."""
    return pontos_atuais + PONTOS_SPRINT[pos_sprint] + PONTOS_CORRIDA[pos_corrida]


def identificar_empate(pts_norris: int, pts_piastri: int, pts_verstappen: int):
    """
    Identifica se há empate na primeira posição.

    Returns:
        Tupla (tipo_empate, pilotos_empatados) ou (None, None) se não há empate no topo.
    """
    pontos = {
        'Norris': pts_norris,
        'Piastri': pts_piastri,
        'Verstappen': pts_verstappen
    }

    max_pontos = max(pontos.values())
    lideres = [piloto for piloto, pts in pontos.items() if pts == max_pontos]

    if len(lideres) >= 2:
        tipo = 'triplo' if len(lideres) == 3 else 'duplo'
        return tipo, ' & '.join(sorted(lideres))

    return None, None


def gerar_cenarios() -> list[dict]:
    """
    Gera todos os cenários válidos onde há empate na primeira posição
    após a penúltima etapa (sprint + corrida).

    Returns:
        Lista de dicionários com dados de cada cenário de empate.
    """
    cenarios = []
    pilotos = PILOTOS_SIMULADOR

    # Produto cartesiano de todas as posições possíveis para os 3 pilotos
    # na sprint e na corrida
    for sprint_nor, sprint_pia, sprint_ver in product(POSICOES_SPRINT, repeat=3):
        # Validar posições da sprint
        if not posicoes_validas(sprint_nor, sprint_pia, sprint_ver):
            continue

        for corrida_nor, corrida_pia, corrida_ver in product(POSICOES_CORRIDA, repeat=3):
            # Validar posições da corrida
            if not posicoes_validas(corrida_nor, corrida_pia, corrida_ver):
                continue

            # Calcular pontos finais
            pts_norris = calcular_pontos(
                pilotos['norris']['pontos'],
                sprint_nor, corrida_nor
            )
            pts_piastri = calcular_pontos(
                pilotos['piastri']['pontos'],
                sprint_pia, corrida_pia
            )
            pts_verstappen = calcular_pontos(
                pilotos['verstappen']['pontos'],
                sprint_ver, corrida_ver
            )

            # Verificar empate na primeira posição
            tipo_empate, pilotos_empatados = identificar_empate(
                pts_norris, pts_piastri, pts_verstappen
            )

            if tipo_empate:
                # Calcular pontos ganhos na etapa
                ganhos_norris = PONTOS_SPRINT[sprint_nor] + PONTOS_CORRIDA[corrida_nor]
                ganhos_piastri = PONTOS_SPRINT[sprint_pia] + PONTOS_CORRIDA[corrida_pia]
                ganhos_verstappen = PONTOS_SPRINT[sprint_ver] + PONTOS_CORRIDA[corrida_ver]
                pontos_empate = max(pts_norris, pts_piastri, pts_verstappen)

                cenarios.append({
                    'sprint_norris': sprint_nor,
                    'sprint_piastri': sprint_pia,
                    'sprint_verstappen': sprint_ver,
                    'corrida_norris': corrida_nor,
                    'corrida_piastri': corrida_pia,
                    'corrida_verstappen': corrida_ver,
                    'pts_norris': pts_norris,
                    'pts_piastri': pts_piastri,
                    'pts_verstappen': pts_verstappen,
                    'ganhos_norris': ganhos_norris,
                    'ganhos_piastri': ganhos_piastri,
                    'ganhos_verstappen': ganhos_verstappen,
                    'pontos_empate': pontos_empate,
                    'tipo_empate': tipo_empate,
                    'pilotos_empatados': pilotos_empatados
                })

    return cenarios


def exportar_csv(cenarios: list[dict], arquivo: Path = None) -> None:
    """Exporta os cenários para arquivo CSV."""
    if arquivo is None:
        arquivo = CSV_PATH

    # Garantir que o diretório existe
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    if not cenarios:
        print("Nenhum cenário de empate encontrado.")
        return

    colunas = [
        'sprint_norris', 'sprint_piastri', 'sprint_verstappen',
        'corrida_norris', 'corrida_piastri', 'corrida_verstappen',
        'pts_norris', 'pts_piastri', 'pts_verstappen',
        'ganhos_norris', 'ganhos_piastri', 'ganhos_verstappen',
        'pontos_empate', 'tipo_empate', 'pilotos_empatados'
    ]

    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(cenarios)

    print(f"Exportado: {arquivo}")
    print(f"Total de cenários: {len(cenarios)}")


def exportar_db(cenarios: list[dict]) -> None:
    """
    Exporta os cenários para o banco de dados DuckDB.

    Args:
        cenarios: Lista de dicionários com os cenários de empate.
    """
    if not cenarios:
        print("Nenhum cenário de empate encontrado.")
        return

    conn = get_connection()
    create_cenarios_empate_table(conn)

    # Limpar tabela antes de inserir
    conn.execute("DELETE FROM cenarios_empate")

    # Inserir em batch usando executemany
    colunas = [
        'sprint_norris', 'sprint_piastri', 'sprint_verstappen',
        'corrida_norris', 'corrida_piastri', 'corrida_verstappen',
        'pts_norris', 'pts_piastri', 'pts_verstappen',
        'ganhos_norris', 'ganhos_piastri', 'ganhos_verstappen',
        'pontos_empate', 'tipo_empate', 'pilotos_empatados'
    ]

    placeholders = ', '.join(['?' for _ in colunas])
    insert_sql = f"INSERT INTO cenarios_empate ({', '.join(colunas)}) VALUES ({placeholders})"

    # Converter lista de dicts para lista de tuplas
    valores = [tuple(c[col] for col in colunas) for c in cenarios]
    conn.executemany(insert_sql, valores)

    conn.close()
    print(f"Exportado para banco de dados: {len(cenarios)} cenários")


def ensure_populated() -> None:
    """
    Garante que a tabela cenarios_empate está populada.

    Se a tabela não existe ou está vazia, gera os cenários e popula o banco.
    Deve ser chamada no início da aplicação.
    """
    conn = get_connection()

    if not is_populated(conn, 'cenarios_empate'):
        print("Banco não populado. Gerando cenários de empate...")
        conn.close()
        cenarios = gerar_cenarios()
        exportar_db(cenarios)
        print("Cenários de empate populados com sucesso!")
    else:
        conn.close()


def imprimir_resumo(cenarios: list[dict]) -> None:
    """Imprime um resumo dos cenários encontrados."""
    if not cenarios:
        print("Nenhum cenário de empate encontrado.")
        return

    triplos = [c for c in cenarios if c['tipo_empate'] == 'triplo']
    duplos = [c for c in cenarios if c['tipo_empate'] == 'duplo']

    print("\n" + "=" * 60)
    print("RESUMO DOS CENÁRIOS DE EMPATE")
    print("=" * 60)
    print(f"\nTotal de cenários: {len(cenarios)}")
    print(f"  - Empates triplos (3 pilotos): {len(triplos)}")
    print(f"  - Empates duplos (2 pilotos): {len(duplos)}")

    # Contar empates duplos por combinação de pilotos
    if duplos:
        print("\nEmpates duplos por combinação:")
        combinacoes = {}
        for c in duplos:
            key = c['pilotos_empatados']
            combinacoes[key] = combinacoes.get(key, 0) + 1
        for combo, count in sorted(combinacoes.items()):
            print(f"  - {combo}: {count} cenários")

    # Mostrar range de pontuações nos empates
    if cenarios:
        pontuacoes = set()
        for c in cenarios:
            max_pts = max(c['pts_norris'], c['pts_piastri'], c['pts_verstappen'])
            pontuacoes.add(max_pts)
        print(f"\nRange de pontuação no empate: {min(pontuacoes)} - {max(pontuacoes)} pts")


# =============================================================================
# EXECUÇÃO VIA CLI
# =============================================================================

if __name__ == '__main__':
    print("Simulador F1 2025 - Cenários de Empate")
    print("-" * 40)
    print("\nClassificação atual:")
    for key, piloto in PILOTOS_SIMULADOR.items():
        print(f"  {piloto['nome']}: {piloto['pontos']} pts")

    print("\nPenúltima etapa: Sprint (máx 8 pts) + Corrida (máx 25 pts)")
    print("\nGerando cenários...")

    cenarios = gerar_cenarios()
    imprimir_resumo(cenarios)
    exportar_csv(cenarios)
