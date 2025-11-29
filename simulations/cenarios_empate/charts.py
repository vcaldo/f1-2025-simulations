"""
Gráficos e visualizações para Cenários de Empate.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import CORES, PILOTOS
from utils.formatters import formatar_posicao


def grafico_barras_combinacoes(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras com contagem por combinação de pilotos.

    Args:
        df: DataFrame com cenários filtrados

    Returns:
        Figura Plotly
    """
    contagem = df['pilotos_empatados'].value_counts().reset_index()
    contagem.columns = ['Pilotos Empatados', 'Cenários']

    fig = px.bar(
        contagem,
        x='Pilotos Empatados',
        y='Cenários',
        color='Pilotos Empatados',
        color_discrete_sequence=CORES['grafico'],
        title='Cenários por Combinação de Pilotos'
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(color=CORES['texto'])
    )

    return fig


def grafico_sunburst(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico sunburst hierárquico: tipo -> pilotos -> faixa de pontos.

    Args:
        df: DataFrame com cenários filtrados

    Returns:
        Figura Plotly
    """
    df_sun = df.copy()
    df_sun['faixa_pontos'] = pd.cut(
        df_sun['pontos_empate'],
        bins=[389, 392, 395, 399, 400],
        labels=['390-392', '393-395', '396-399', '400+']
    )

    fig = px.sunburst(
        df_sun,
        path=['tipo_empate', 'pilotos_empatados', 'faixa_pontos'],
        color='tipo_empate',
        color_discrete_map={'triplo': CORES['destaque'], 'duplo': CORES['norris']},
        title='Hierarquia: Tipo → Pilotos → Faixa de Pontos'
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CORES['texto'])
    )

    return fig


def grafico_heatmap_posicoes(df: pd.DataFrame, piloto: str) -> go.Figure:
    """
    Heatmap de frequência sprint x corrida para um piloto.

    Args:
        df: DataFrame com cenários filtrados
        piloto: Nome do piloto (ex: 'Norris')

    Returns:
        Figura Plotly
    """
    col_sprint = f'sprint_{piloto.lower()}'
    col_corrida = f'corrida_{piloto.lower()}'

    # Criar tabela de frequência
    heatmap_data = df.groupby([col_sprint, col_corrida]).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index=col_sprint, columns=col_corrida, values='count').fillna(0)

    # Renomear índices para exibição
    heatmap_pivot.index = [formatar_posicao(p) for p in heatmap_pivot.index]
    heatmap_pivot.columns = [formatar_posicao(p) for p in heatmap_pivot.columns]

    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x='Posição Corrida', y='Posição Sprint', color='Cenários'),
        color_continuous_scale=['#F5F5F5', PILOTOS[piloto]['cor']],
        title=f'Frequência de Posições - {piloto}'
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CORES['texto'])
    )

    return fig


def grafico_pontos_ganhos(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico box plot: pontos ganhos por cada piloto na etapa.

    Args:
        df: DataFrame com cenários filtrados

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    for piloto, dados in PILOTOS.items():
        col = f'ganhos_{piloto.lower()}'
        if col in df.columns:
            fig.add_trace(go.Box(
                y=df[col],
                name=piloto,
                marker_color=dados['cor'],
                boxpoints='outliers'
            ))

    fig.update_layout(
        title='Distribuição de Pontos Ganhos na Etapa',
        yaxis_title='Pontos Ganhos',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CORES['texto'])
    )

    return fig
