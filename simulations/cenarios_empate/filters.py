"""
Filtros e métricas para o dashboard de Cenários de Empate.
Utiliza SQL parametrizado para queries no DuckDB.
"""

import streamlit as st
import pandas as pd

from database import get_connection


@st.cache_resource
def _get_db_connection():
    """Retorna conexão cacheada com o banco."""
    return get_connection()


@st.cache_data
def carregar_opcoes_filtros() -> dict:
    """
    Carrega opções únicas para os filtros da sidebar.

    Returns:
        Dicionário com listas de opções para cada filtro.
    """
    conn = _get_db_connection()

    tipos = conn.execute(
        "SELECT DISTINCT tipo_empate FROM cenarios_empate ORDER BY tipo_empate"
    ).fetchall()

    combinacoes = conn.execute(
        "SELECT DISTINCT pilotos_empatados FROM cenarios_empate ORDER BY pilotos_empatados"
    ).fetchall()

    pontos_range = conn.execute(
        "SELECT MIN(pontos_empate), MAX(pontos_empate) FROM cenarios_empate"
    ).fetchone()

    return {
        'tipos': [t[0] for t in tipos],
        'combinacoes': [c[0] for c in combinacoes],
        'pontos_min': pontos_range[0],
        'pontos_max': pontos_range[1]
    }


@st.cache_data
def carregar_dados_filtrados(
    tipo_empate: str | None = None,
    pilotos_empatados: str | None = None,
    pontos_min: int | None = None,
    pontos_max: int | None = None
) -> pd.DataFrame:
    """
    Carrega dados filtrados do banco usando SQL parametrizado.

    Args:
        tipo_empate: Filtro por tipo de empate (duplo/triplo)
        pilotos_empatados: Filtro por combinação de pilotos
        pontos_min: Pontos mínimos do empate
        pontos_max: Pontos máximos do empate

    Returns:
        DataFrame com os cenários filtrados.
    """
    conn = _get_db_connection()

    # Construir query dinamicamente
    conditions = []
    params = []

    if tipo_empate:
        conditions.append("tipo_empate = ?")
        params.append(tipo_empate)

    if pilotos_empatados:
        conditions.append("pilotos_empatados = ?")
        params.append(pilotos_empatados)

    if pontos_min is not None:
        conditions.append("pontos_empate >= ?")
        params.append(pontos_min)

    if pontos_max is not None:
        conditions.append("pontos_empate <= ?")
        params.append(pontos_max)

    query = "SELECT * FROM cenarios_empate"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return conn.execute(query, params).df()


@st.cache_data
def carregar_total_cenarios() -> int:
    """Retorna o total de cenários no banco."""
    conn = _get_db_connection()
    return conn.execute("SELECT COUNT(*) FROM cenarios_empate").fetchone()[0]


def sidebar_filtros() -> pd.DataFrame:
    """
    Cria filtros na sidebar e retorna DataFrame filtrado via SQL.

    Returns:
        DataFrame filtrado com base nas seleções
    """
    st.sidebar.header("🔍 Filtros")

    # Carregar opções dos filtros
    opcoes = carregar_opcoes_filtros()

    # Filtro tipo de empate
    tipos = ['Todos'] + opcoes['tipos']
    tipo_selecionado = st.sidebar.selectbox("Tipo de Empate", tipos)

    # Filtro pilotos empatados
    combinacoes = ['Todas'] + opcoes['combinacoes']
    combinacao_selecionada = st.sidebar.selectbox("Pilotos Empatados", combinacoes)

    # Filtro faixa de pontos
    min_pts, max_pts = opcoes['pontos_min'], opcoes['pontos_max']
    faixa_pts = st.sidebar.slider(
        "Faixa de Pontos do Empate",
        min_pts, max_pts, (min_pts, max_pts)
    )

    # Carregar dados filtrados via SQL
    df_filtrado = carregar_dados_filtrados(
        tipo_empate=tipo_selecionado if tipo_selecionado != 'Todos' else None,
        pilotos_empatados=combinacao_selecionada if combinacao_selecionada != 'Todas' else None,
        pontos_min=faixa_pts[0],
        pontos_max=faixa_pts[1]
    )

    return df_filtrado


def metricas_resumo(df_filtrado: pd.DataFrame) -> None:
    """
    Exibe métricas resumo dos cenários filtrados.

    Args:
        df_filtrado: DataFrame após aplicação de filtros
    """
    total = carregar_total_cenarios()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total de Cenários",
            len(df_filtrado),
            f"{len(df_filtrado) - total} do total" if len(df_filtrado) != total else None
        )

    with col2:
        triplos = len(df_filtrado[df_filtrado['tipo_empate'] == 'triplo'])
        st.metric("Empates Triplos", triplos)

    with col3:
        duplos = len(df_filtrado[df_filtrado['tipo_empate'] == 'duplo'])
        st.metric("Empates Duplos", duplos)

    with col4:
        if len(df_filtrado) > 0:
            pts_range = f"{df_filtrado['pontos_empate'].min()} - {df_filtrado['pontos_empate'].max()}"
        else:
            pts_range = "-"
        st.metric("Range de Pontos", pts_range)
