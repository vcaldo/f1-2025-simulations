"""
Simulador de Cenários de Campeão F1 2025 - Versão Otimizada.

Calcula todas as combinações possíveis de resultados nas corridas restantes
(Sprint Qatar, Race Qatar, Race Abu Dhabi) para determinar cenários de campeonato.

Usa abordagem de agregação por convolução para máxima eficiência:
- Agrupa por (delta_pontos, delta_vitorias) únicos por piloto
- Reduz de ~550M combinações brutas para ~dezenas de milhares de estados únicos
- Armazena também contagem de segundos/terceiros para tie-break completo
"""

from itertools import product
from dataclasses import dataclass
from collections import Counter
import duckdb

from config.settings import PONTOS_SPRINT, PONTOS_CORRIDA


# =============================================================================
# CONSTANTES - CLASSIFICAÇÃO ATUAL (28/11/2025)
# =============================================================================

# Pontos atuais
PONTOS_ATUAIS = {
    'norris': 390,
    'piastri': 366,
    'verstappen': 366,
}

# Vitórias atuais (do prompt: 7, 7, 6)
VITORIAS_ATUAIS = {
    'norris': 7,
    'piastri': 7,
    'verstappen': 6,
}

# Segundos lugares atuais (estimativa baseada em podiums)
# Norris: 17 podios, 7 wins = 10 outros pódios
# Piastri: 14 podios, 7 wins = 7 outros pódios
# Verstappen: 13 podios, 6 wins = 7 outros pódios
SEGUNDOS_ATUAIS = {
    'norris': 6,
    'piastri': 4,
    'verstappen': 4,
}

TERCEIROS_ATUAIS = {
    'norris': 4,
    'piastri': 3,
    'verstappen': 3,
}

PILOTOS = ['norris', 'piastri', 'verstappen']

# Posições que pontuam
POSICOES_SPRINT = [1, 2, 3, 4, 5, 6, 7, 8]
POSICOES_CORRIDA = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Código para "fora dos pontos"
FORA_PONTOS = 99


# =============================================================================
# ESTRUTURAS DE DADOS SIMPLIFICADAS
# =============================================================================

@dataclass(frozen=True)
class Delta:
    """Delta de um evento para um piloto."""
    pontos: int
    vitoria: int  # 0 ou 1
    segundo: int  # 0 ou 1
    terceiro: int  # 0 ou 1


@dataclass(frozen=True)
class DeltaTrio:
    """Delta combinado para os 3 pilotos."""
    norris: Delta
    piastri: Delta
    verstappen: Delta


# =============================================================================
# GERAÇÃO DE DELTAS
# =============================================================================

def posicao_para_delta(posicao: int, tabela_pontos: dict) -> Delta:
    """Converte posição em delta de stats."""
    return Delta(
        pontos=tabela_pontos.get(posicao, 0),
        vitoria=1 if posicao == 1 else 0,
        segundo=1 if posicao == 2 else 0,
        terceiro=1 if posicao == 3 else 0,
    )


def gerar_deltas_evento(posicoes: list[int], tabela_pontos: dict) -> list[DeltaTrio]:
    """
    Gera todos os deltas válidos para um evento.

    Regras:
    - Cada piloto pode ficar em qualquer posição que pontua OU fora dos pontos (99)
    - Se dois ou mais pilotos pontuam, não podem ter a mesma posição
    """
    todas_posicoes = posicoes + [FORA_PONTOS]
    deltas = []

    for pos_n, pos_p, pos_v in product(todas_posicoes, repeat=3):
        # Verificar posições não repetidas (exceto FORA_PONTOS)
        posicoes_dentro = [p for p in [pos_n, pos_p, pos_v] if p != FORA_PONTOS]
        if len(posicoes_dentro) != len(set(posicoes_dentro)):
            continue

        deltas.append(DeltaTrio(
            norris=posicao_para_delta(pos_n, tabela_pontos),
            piastri=posicao_para_delta(pos_p, tabela_pontos),
            verstappen=posicao_para_delta(pos_v, tabela_pontos),
        ))

    return deltas


def somar_deltas(d1: Delta, d2: Delta) -> Delta:
    """Soma dois deltas de um piloto."""
    return Delta(
        pontos=d1.pontos + d2.pontos,
        vitoria=d1.vitoria + d2.vitoria,
        segundo=d1.segundo + d2.segundo,
        terceiro=d1.terceiro + d2.terceiro,
    )


def somar_delta_trios(t1: DeltaTrio, t2: DeltaTrio) -> DeltaTrio:
    """Soma dois DeltaTrios."""
    return DeltaTrio(
        norris=somar_deltas(t1.norris, t2.norris),
        piastri=somar_deltas(t1.piastri, t2.piastri),
        verstappen=somar_deltas(t1.verstappen, t2.verstappen),
    )


# =============================================================================
# DETERMINAÇÃO DO CAMPEÃO
# =============================================================================

def determinar_campeao(
    pts: tuple[int, int, int],
    wins: tuple[int, int, int],
    seconds: tuple[int, int, int],
    thirds: tuple[int, int, int],
) -> tuple[str, str]:
    """
    Determina o campeão usando sistema de tie-break da F1.

    Ordem de critérios:
    1. Mais pontos
    2. Mais vitórias
    3. Mais segundos lugares
    4. Mais terceiros lugares

    Args:
        pts: (norris, piastri, verstappen) pontos finais
        wins: (norris, piastri, verstappen) vitórias finais
        seconds: (norris, piastri, verstappen) segundos lugares finais
        thirds: (norris, piastri, verstappen) terceiros lugares finais

    Returns:
        (campeao, metodo): nome do piloto e critério decisivo
    """
    pilotos = ['norris', 'piastri', 'verstappen']

    # Criar tupla de ranking (maior é melhor)
    stats = [
        (pts[i], wins[i], seconds[i], thirds[i], pilotos[i])
        for i in range(3)
    ]

    # Ordenar por todos os critérios (descendente)
    stats.sort(reverse=True)

    primeiro = stats[0]
    segundo = stats[1]

    # Determinar método de decisão
    if primeiro[0] > segundo[0]:
        metodo = 'pontos'
    elif primeiro[1] > segundo[1]:
        metodo = 'vitorias'
    elif primeiro[2] > segundo[2]:
        metodo = 'segundos_lugares'
    elif primeiro[3] > segundo[3]:
        metodo = 'terceiros_lugares'
    else:
        metodo = 'empate_total'

    return primeiro[4], metodo


# =============================================================================
# SIMULAÇÃO POR CONVOLUÇÃO
# =============================================================================

def simular_cenarios() -> list[dict]:
    """
    Simula todos os cenários usando convolução de deltas.

    Fases:
    1. Gera deltas para Sprint Qatar, Race Qatar, Race Abu Dhabi
    2. Convolui Sprint + Race Qatar → estados intermediários
    3. Convolui intermediários + Abu Dhabi → estados finais
    4. Determina campeão para cada estado final

    Returns:
        Lista de cenários com deltas, pontuação final e campeão
    """
    print("=" * 60)
    print("SIMULAÇÃO DE CENÁRIOS DE CAMPEONATO F1 2025")
    print("=" * 60)

    # Gerar deltas para cada evento
    print("\n[1/4] Gerando deltas por evento...")
    deltas_sprint = gerar_deltas_evento(POSICOES_SPRINT, PONTOS_SPRINT)
    deltas_corrida = gerar_deltas_evento(POSICOES_CORRIDA, PONTOS_CORRIDA)

    print(f"  Sprint Qatar: {len(deltas_sprint)} combinações")
    print(f"  Race Qatar: {len(deltas_corrida)} combinações")
    print(f"  Race Abu Dhabi: {len(deltas_corrida)} combinações")
    print(f"  Espaço bruto: {len(deltas_sprint) * len(deltas_corrida) ** 2:,}")

    # Fase 1: Convolução Sprint Qatar + Race Qatar
    print("\n[2/4] Convoluindo Sprint Qatar + Race Qatar...")
    estados_qatar: Counter[DeltaTrio] = Counter()

    for ds in deltas_sprint:
        for dr in deltas_corrida:
            delta_combinado = somar_delta_trios(ds, dr)
            estados_qatar[delta_combinado] += 1

    print(f"  Estados únicos após Qatar: {len(estados_qatar):,}")

    # Fase 2: Convolução com Abu Dhabi
    print("\n[3/4] Convoluindo com Race Abu Dhabi...")
    estados_finais: Counter[DeltaTrio] = Counter()

    for delta_qatar, count_qatar in estados_qatar.items():
        for da in deltas_corrida:
            delta_final = somar_delta_trios(delta_qatar, da)
            estados_finais[delta_final] += count_qatar

    print(f"  Estados finais únicos: {len(estados_finais):,}")

    # Fase 3: Determinar campeão para cada estado
    print("\n[4/4] Determinando campeão para cada estado...")
    cenarios = []

    for delta, num_combinacoes in estados_finais.items():
        # Calcular stats finais
        pts_final = (
            PONTOS_ATUAIS['norris'] + delta.norris.pontos,
            PONTOS_ATUAIS['piastri'] + delta.piastri.pontos,
            PONTOS_ATUAIS['verstappen'] + delta.verstappen.pontos,
        )
        wins_final = (
            VITORIAS_ATUAIS['norris'] + delta.norris.vitoria,
            VITORIAS_ATUAIS['piastri'] + delta.piastri.vitoria,
            VITORIAS_ATUAIS['verstappen'] + delta.verstappen.vitoria,
        )
        seconds_final = (
            SEGUNDOS_ATUAIS['norris'] + delta.norris.segundo,
            SEGUNDOS_ATUAIS['piastri'] + delta.piastri.segundo,
            SEGUNDOS_ATUAIS['verstappen'] + delta.verstappen.segundo,
        )
        thirds_final = (
            TERCEIROS_ATUAIS['norris'] + delta.norris.terceiro,
            TERCEIROS_ATUAIS['piastri'] + delta.piastri.terceiro,
            TERCEIROS_ATUAIS['verstappen'] + delta.verstappen.terceiro,
        )

        campeao, metodo = determinar_campeao(pts_final, wins_final, seconds_final, thirds_final)

        cenarios.append({
            # Deltas
            'delta_pts_norris': delta.norris.pontos,
            'delta_pts_piastri': delta.piastri.pontos,
            'delta_pts_verstappen': delta.verstappen.pontos,
            'delta_wins_norris': delta.norris.vitoria,
            'delta_wins_piastri': delta.piastri.vitoria,
            'delta_wins_verstappen': delta.verstappen.vitoria,
            # Finais
            'pts_final_norris': pts_final[0],
            'pts_final_piastri': pts_final[1],
            'pts_final_verstappen': pts_final[2],
            'wins_final_norris': wins_final[0],
            'wins_final_piastri': wins_final[1],
            'wins_final_verstappen': wins_final[2],
            # Resultado
            'campeao': campeao,
            'metodo_decisao': metodo,
            'num_combinacoes': num_combinacoes,
        })

    total_comb = sum(c['num_combinacoes'] for c in cenarios)
    print(f"\n  Total de estados únicos: {len(cenarios):,}")
    print(f"  Total de combinações representadas: {total_comb:,}")

    return cenarios


# =============================================================================
# BANCO DE DADOS
# =============================================================================

def criar_tabela(conn: duckdb.DuckDBPyConnection) -> None:
    """Cria tabela cenarios_campeao."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cenarios_campeao (
            delta_pts_norris INTEGER,
            delta_pts_piastri INTEGER,
            delta_pts_verstappen INTEGER,
            delta_wins_norris INTEGER,
            delta_wins_piastri INTEGER,
            delta_wins_verstappen INTEGER,
            pts_final_norris INTEGER,
            pts_final_piastri INTEGER,
            pts_final_verstappen INTEGER,
            wins_final_norris INTEGER,
            wins_final_piastri INTEGER,
            wins_final_verstappen INTEGER,
            campeao VARCHAR,
            metodo_decisao VARCHAR,
            num_combinacoes INTEGER
        )
    """)


def popular_banco(conn: duckdb.DuckDBPyConnection, cenarios: list[dict]) -> None:
    """Popula banco via DataFrame para máxima performance."""
    import pandas as pd

    print("\nPopulando banco de dados...")
    df = pd.DataFrame(cenarios)
    conn.execute("INSERT INTO cenarios_campeao SELECT * FROM df")
    conn.commit()
    print(f"  Inseridos {len(cenarios):,} estados.")


def gerar_estatisticas(conn: duckdb.DuckDBPyConnection) -> dict:
    """Gera estatísticas dos cenários."""
    stats = {}

    # Totais
    result = conn.execute("""
        SELECT COUNT(*) as estados, SUM(num_combinacoes) as combinacoes
        FROM cenarios_campeao
    """).fetchone()
    stats['total_estados'] = result[0]
    stats['total_combinacoes'] = result[1]

    # Por campeão
    stats['por_campeao'] = conn.execute("""
        SELECT campeao,
               SUM(num_combinacoes) as combinacoes,
               COUNT(*) as estados,
               ROUND(100.0 * SUM(num_combinacoes) /
                     (SELECT SUM(num_combinacoes) FROM cenarios_campeao), 4) as chance
        FROM cenarios_campeao
        GROUP BY campeao
        ORDER BY combinacoes DESC
    """).fetchall()

    # Por método
    stats['por_metodo'] = conn.execute("""
        SELECT metodo_decisao,
               SUM(num_combinacoes) as combinacoes,
               COUNT(*) as estados
        FROM cenarios_campeao
        GROUP BY metodo_decisao
        ORDER BY combinacoes DESC
    """).fetchall()

    # Campeão + método
    stats['campeao_metodo'] = conn.execute("""
        SELECT campeao, metodo_decisao,
               SUM(num_combinacoes) as combinacoes
        FROM cenarios_campeao
        GROUP BY campeao, metodo_decisao
        ORDER BY campeao, combinacoes DESC
    """).fetchall()

    return stats


def imprimir_estatisticas(stats: dict) -> None:
    """Imprime estatísticas formatadas."""
    print("\n" + "=" * 70)
    print("RESULTADOS DA SIMULAÇÃO")
    print("=" * 70)

    print(f"\nEstados únicos analisados: {stats['total_estados']:,}")
    print(f"Combinações de corridas representadas: {stats['total_combinacoes']:,}")

    print("\n" + "-" * 70)
    print("CHANCES DE TÍTULO")
    print("-" * 70)
    print(f"{'Piloto':<15} {'Combinações':>18} {'Estados':>12} {'Chance':>12}")
    print("-" * 70)

    for campeao, comb, estados, chance in stats['por_campeao']:
        nome = campeao.capitalize()
        print(f"{nome:<15} {comb:>18,} {estados:>12,} {chance:>11.2f}%")

    print("\n" + "-" * 70)
    print("POR MÉTODO DE DECISÃO")
    print("-" * 70)

    for metodo, comb, estados in stats['por_metodo']:
        pct = 100.0 * comb / stats['total_combinacoes']
        print(f"  {metodo:<25}: {comb:>15,} ({pct:.2f}%)")

    print("\n" + "-" * 70)
    print("DETALHAMENTO CAMPEÃO × MÉTODO")
    print("-" * 70)

    campeao_atual = None
    for campeao, metodo, comb in stats['campeao_metodo']:
        if campeao != campeao_atual:
            print(f"\n  {campeao.capitalize()}:")
            campeao_atual = campeao
        pct = 100.0 * comb / stats['total_combinacoes']
        print(f"    {metodo:<22}: {comb:>12,} ({pct:.2f}%)")


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================

def criar_views_agregadas(conn: duckdb.DuckDBPyConnection) -> None:
    """Cria views agregadas para consultas rápidas."""

    # View: resumo por campeão
    conn.execute("""
        CREATE OR REPLACE VIEW v_resumo_campeao AS
        SELECT
            campeao,
            SUM(num_combinacoes) as total_combinacoes,
            COUNT(*) as total_estados,
            ROUND(100.0 * SUM(num_combinacoes) /
                  (SELECT SUM(num_combinacoes) FROM cenarios_campeao), 2) as chance_pct
        FROM cenarios_campeao
        GROUP BY campeao
        ORDER BY total_combinacoes DESC
    """)

    # View: resumo por método de decisão
    conn.execute("""
        CREATE OR REPLACE VIEW v_resumo_metodo AS
        SELECT
            metodo_decisao,
            SUM(num_combinacoes) as total_combinacoes,
            ROUND(100.0 * SUM(num_combinacoes) /
                  (SELECT SUM(num_combinacoes) FROM cenarios_campeao), 2) as pct
        FROM cenarios_campeao
        GROUP BY metodo_decisao
        ORDER BY total_combinacoes DESC
    """)

    # View: cenários de empate em pontos (decisão por vitórias ou além)
    conn.execute("""
        CREATE OR REPLACE VIEW v_cenarios_empate AS
        SELECT *
        FROM cenarios_campeao
        WHERE metodo_decisao != 'pontos'
        ORDER BY num_combinacoes DESC
    """)

    print("Views agregadas criadas: v_resumo_campeao, v_resumo_metodo, v_cenarios_empate")


def executar(conn: duckdb.DuckDBPyConnection, force: bool = False) -> dict:
    """
    Executa simulação completa.

    Args:
        conn: Conexão DuckDB
        force: Se True, recalcula mesmo que dados existam

    Returns:
        Estatísticas da simulação
    """
    from database.connection import is_populated

    tabela = 'cenarios_campeao'

    # Verificar se já está populado
    if not force and is_populated(conn, tabela):
        print(f"Tabela '{tabela}' já populada. Use force=True para recalcular.")
        return gerar_estatisticas(conn)

    # Recriar tabela
    conn.execute(f"DROP TABLE IF EXISTS {tabela}")
    criar_tabela(conn)

    # Simular
    cenarios = simular_cenarios()

    # Popular
    popular_banco(conn, cenarios)

    # Criar views
    criar_views_agregadas(conn)

    # Estatísticas
    stats = gerar_estatisticas(conn)
    imprimir_estatisticas(stats)

    return stats


if __name__ == '__main__':
    from database.connection import get_connection

    conn = get_connection()
    try:
        executar(conn, force=True)
    finally:
        conn.close()
