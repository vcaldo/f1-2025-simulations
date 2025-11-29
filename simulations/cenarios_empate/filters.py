"""
Filtros e métricas para o dashboard de Cenários de Empate.
"""

import streamlit as st
import pandas as pd


def sidebar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria filtros na sidebar e retorna DataFrame filtrado.

    Args:
        df: DataFrame original com todos os cenários

    Returns:
        DataFrame filtrado com base nas seleções
    """
    st.sidebar.header("🔍 Filtros")

    # Filtro tipo de empate
    tipos = ['Todos'] + list(df['tipo_empate'].unique())
    tipo_selecionado = st.sidebar.selectbox("Tipo de Empate", tipos)

    # Filtro pilotos empatados
    combinacoes = ['Todas'] + sorted(df['pilotos_empatados'].unique().tolist())
    combinacao_selecionada = st.sidebar.selectbox("Pilotos Empatados", combinacoes)

    # Filtro faixa de pontos
    min_pts, max_pts = int(df['pontos_empate'].min()), int(df['pontos_empate'].max())
    faixa_pts = st.sidebar.slider(
        "Faixa de Pontos do Empate",
        min_pts, max_pts, (min_pts, max_pts)
    )

    # Aplicar filtros
    df_filtrado = df.copy()

    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tipo_empate'] == tipo_selecionado]

    if combinacao_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['pilotos_empatados'] == combinacao_selecionada]

    df_filtrado = df_filtrado[
        (df_filtrado['pontos_empate'] >= faixa_pts[0]) &
        (df_filtrado['pontos_empate'] <= faixa_pts[1])
    ]

    return df_filtrado


def metricas_resumo(df_filtrado: pd.DataFrame, df_total: pd.DataFrame) -> None:
    """
    Exibe métricas resumo dos cenários filtrados.

    Args:
        df_filtrado: DataFrame após aplicação de filtros
        df_total: DataFrame original completo
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total de Cenários",
            len(df_filtrado),
            f"{len(df_filtrado) - len(df_total)} do total" if len(df_filtrado) != len(df_total) else None
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
