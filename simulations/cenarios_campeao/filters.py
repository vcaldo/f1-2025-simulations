"""
Módulo de filtros e carregamento de dados para Cenários de Campeão F1 2025.
Gerencia conexão com banco, filtros da sidebar e funções auxiliares.
"""

import streamlit as st
import pandas as pd
import duckdb

from database.connection import get_connection


# =============================================================================
# LABELS AMIGÁVEIS
# =============================================================================

LABELS_METODO = {
    'pontos': 'Por Pontos',
    'vitorias': 'Por Vitórias',
    'segundos_lugares': 'Por 2º Lugares',
    'terceiros_lugares': 'Por 3º Lugares',
    'empate_total': 'Empate Total',
}

LABELS_PILOTO = {
    'norris': 'Lando Norris',
    'piastri': 'Oscar Piastri',
    'verstappen': 'Max Verstappen',
}

LABELS_POSICAO = {
    1: '1º', 2: '2º', 3: '3º', 4: '4º', 5: '5º',
    6: '6º', 7: '7º', 8: '8º', 9: '9º', 10: '10º',
    99: 'Fora dos pontos',
}


def label_metodo(metodo: str) -> str:
    """Retorna label amigável para método de decisão."""
    return LABELS_METODO.get(metodo, metodo)


def label_piloto(piloto: str) -> str:
    """Retorna label amigável para piloto."""
    return LABELS_PILOTO.get(piloto.lower(), piloto.capitalize())


def label_posicao(posicao: int) -> str:
    """Retorna label amigável para posição."""
    return LABELS_POSICAO.get(posicao, str(posicao))


# =============================================================================
# CONEXÃO CACHE
# =============================================================================

@st.cache_resource
def get_db_connection():
    """Retorna conexão com banco de dados (cacheada)."""
    return get_connection()


# =============================================================================
# CARREGAMENTO DE DADOS
# =============================================================================

@st.cache_data(ttl=300)
def carregar_estatisticas_resumo() -> dict:
    """
    Carrega estatísticas resumo do banco.

    Returns:
        Dicionário com estatísticas por campeão e totais
    """
    conn = get_db_connection()

    # Total geral
    totais = conn.execute("""
        SELECT COUNT(*) as estados, SUM(num_combinacoes) as combinacoes
        FROM cenarios_campeao
    """).fetchone()

    # Por campeão
    por_campeao = conn.execute("""
        SELECT
            campeao,
            SUM(num_combinacoes) as combinacoes,
            COUNT(*) as estados,
            ROUND(100.0 * SUM(num_combinacoes) /
                  (SELECT SUM(num_combinacoes) FROM cenarios_campeao), 2) as chance
        FROM cenarios_campeao
        GROUP BY campeao
        ORDER BY combinacoes DESC
    """).fetchdf()

    # Por método
    por_metodo = conn.execute("""
        SELECT
            metodo_decisao,
            SUM(num_combinacoes) as combinacoes,
            ROUND(100.0 * SUM(num_combinacoes) /
                  (SELECT SUM(num_combinacoes) FROM cenarios_campeao), 2) as pct
        FROM cenarios_campeao
        GROUP BY metodo_decisao
        ORDER BY combinacoes DESC
    """).fetchdf()

    # Campeão x Método
    campeao_metodo = conn.execute("""
        SELECT
            campeao,
            metodo_decisao,
            SUM(num_combinacoes) as combinacoes,
            ROUND(100.0 * SUM(num_combinacoes) /
                  (SELECT SUM(num_combinacoes) FROM cenarios_campeao), 4) as pct
        FROM cenarios_campeao
        GROUP BY campeao, metodo_decisao
        ORDER BY campeao, combinacoes DESC
    """).fetchdf()

    return {
        'total_estados': totais[0],
        'total_combinacoes': totais[1],
        'por_campeao': por_campeao,
        'por_metodo': por_metodo,
        'campeao_metodo': campeao_metodo,
    }


@st.cache_data(ttl=300)
def carregar_distribuicao_pontos() -> pd.DataFrame:
    """
    Carrega distribuição de pontos finais por piloto.

    Returns:
        DataFrame com ranges de pontos e contagens ponderadas
    """
    conn = get_db_connection()

    df = conn.execute("""
        SELECT
            pts_final_norris,
            pts_final_piastri,
            pts_final_verstappen,
            num_combinacoes
        FROM cenarios_campeao
    """).fetchdf()

    return df


@st.cache_data(ttl=300)
def carregar_cenarios_vitoria(piloto: str) -> pd.DataFrame:
    """
    Carrega cenários em que um piloto específico é campeão.

    Args:
        piloto: Nome do piloto (lowercase)

    Returns:
        DataFrame filtrado
    """
    conn = get_db_connection()

    df = conn.execute(f"""
        SELECT *
        FROM cenarios_campeao
        WHERE campeao = '{piloto}'
        ORDER BY num_combinacoes DESC
    """).fetchdf()

    return df


@st.cache_data(ttl=300)
def carregar_cenarios_filtrados(
    campeao: str | None = None,
    metodo: str | None = None,
    pts_min: int | None = None,
    pts_max: int | None = None,
) -> pd.DataFrame:
    """
    Carrega cenários com filtros aplicados.

    Args:
        campeao: Filtrar por campeão
        metodo: Filtrar por método de decisão
        pts_min: Pontos mínimos do campeão
        pts_max: Pontos máximos do campeão

    Returns:
        DataFrame filtrado
    """
    conn = get_db_connection()

    conditions = []
    if campeao:
        conditions.append(f"campeao = '{campeao}'")
    if metodo:
        conditions.append(f"metodo_decisao = '{metodo}'")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # Adicionar filtro de pontos (requer CASE para pegar pontos do campeão)
    if pts_min is not None or pts_max is not None:
        pts_filter = """
            CASE campeao
                WHEN 'norris' THEN pts_final_norris
                WHEN 'piastri' THEN pts_final_piastri
                WHEN 'verstappen' THEN pts_final_verstappen
            END
        """
        if where_clause:
            if pts_min is not None:
                where_clause += f" AND {pts_filter} >= {pts_min}"
            if pts_max is not None:
                where_clause += f" AND {pts_filter} <= {pts_max}"
        else:
            parts = []
            if pts_min is not None:
                parts.append(f"{pts_filter} >= {pts_min}")
            if pts_max is not None:
                parts.append(f"{pts_filter} <= {pts_max}")
            where_clause = "WHERE " + " AND ".join(parts)

    query = f"""
        SELECT *
        FROM cenarios_campeao
        {where_clause}
        ORDER BY num_combinacoes DESC
        LIMIT 10000
    """

    return conn.execute(query).fetchdf()


@st.cache_data(ttl=300)
def carregar_opcoes_filtros() -> dict:
    """
    Carrega opções disponíveis para filtros.

    Returns:
        Dicionário com listas de opções
    """
    conn = get_db_connection()

    # Métodos disponíveis
    metodos = conn.execute("""
        SELECT DISTINCT metodo_decisao FROM cenarios_campeao ORDER BY metodo_decisao
    """).fetchdf()['metodo_decisao'].tolist()

    # Range de pontos
    pontos = conn.execute("""
        SELECT
            MIN(LEAST(pts_final_norris, pts_final_piastri, pts_final_verstappen)) as pts_min,
            MAX(GREATEST(pts_final_norris, pts_final_piastri, pts_final_verstappen)) as pts_max
        FROM cenarios_campeao
    """).fetchone()

    return {
        'metodos': metodos,
        'pontos_min': pontos[0],
        'pontos_max': pontos[1],
        'campeoes': ['norris', 'piastri', 'verstappen'],
    }


# =============================================================================
# SIDEBAR FILTROS
# =============================================================================

def sidebar_filtros() -> dict:
    """
    Cria filtros na sidebar e retorna seleções.

    Returns:
        Dicionário com valores selecionados
    """
    st.sidebar.header("🔍 Filtros")

    opcoes = carregar_opcoes_filtros()

    # Filtro por campeão
    campeoes_opcoes = ['Todos'] + [label_piloto(p) for p in opcoes['campeoes']]
    campeao_label = st.sidebar.selectbox("Campeão", campeoes_opcoes)
    campeao = None
    if campeao_label != 'Todos':
        # Converter label de volta para key
        for k, v in LABELS_PILOTO.items():
            if v == campeao_label:
                campeao = k
                break

    # Filtro por método
    metodos_opcoes = ['Todos'] + [label_metodo(m) for m in opcoes['metodos']]
    metodo_label = st.sidebar.selectbox("Método de Decisão", metodos_opcoes)
    metodo = None
    if metodo_label != 'Todos':
        for k, v in LABELS_METODO.items():
            if v == metodo_label:
                metodo = k
                break

    return {
        'campeao': campeao,
        'metodo': metodo,
    }


# =============================================================================
# MÉTRICAS RESUMO
# =============================================================================

def metricas_resumo() -> None:
    """Exibe métricas resumo no topo da página."""
    stats = carregar_estatisticas_resumo()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Combinações",
            f"{stats['total_combinacoes']:,}".replace(',', '.'),
            help="Número total de combinações de resultados possíveis"
        )

    with col2:
        st.metric(
            "Estados Únicos",
            f"{stats['total_estados']:,}".replace(',', '.'),
            help="Estados distintos após agregação por deltas"
        )

    # Chances por piloto nas colunas restantes
    df_campeao = stats['por_campeao']

    if len(df_campeao) >= 1:
        row = df_campeao.iloc[0]
        with col3:
            st.metric(
                f"🏆 {label_piloto(row['campeao'])}",
                f"{row['chance']:.2f}%",
                help="Maior chance de título"
            )

    if len(df_campeao) >= 2:
        row = df_campeao.iloc[1]
        with col4:
            st.metric(
                f"2º {label_piloto(row['campeao'])}",
                f"{row['chance']:.2f}%"
            )


def cards_chances() -> None:
    """Exibe cards com chances de cada piloto."""
    stats = carregar_estatisticas_resumo()
    df = stats['por_campeao']

    cols = st.columns(3)

    from config.settings import CORES

    cores_piloto = {
        'norris': CORES['norris'],
        'piastri': CORES['piastri'],
        'verstappen': CORES['verstappen'],
    }

    for i, (_, row) in enumerate(df.iterrows()):
        piloto = row['campeao']
        cor = cores_piloto.get(piloto, '#888888')

        with cols[i]:
            st.markdown(f"""
            <div style="
                background: {cor}40;
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid {cor};
                text-align: center;
            ">
                <h2 style="margin: 0; color: #4A4A4A;">{label_piloto(piloto)}</h2>
                <p style="font-size: 42px; font-weight: bold; margin: 10px 0; color: {cor};">
                    {row['chance']:.2f}%
                </p>
                <p style="font-size: 14px; color: #666; margin: 0;">
                    {int(row['combinacoes']):,} combinações
                </p>
            </div>
            """.replace(',', '.'), unsafe_allow_html=True)
