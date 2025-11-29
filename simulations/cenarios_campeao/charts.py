"""
Módulo de gráficos para Cenários de Campeão F1 2025.
Contém funções para criar visualizações Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from config.settings import CORES
from simulations.cenarios_campeao.filters import (
    label_metodo,
    label_piloto,
    carregar_estatisticas_resumo,
    carregar_distribuicao_pontos,
)


# =============================================================================
# PALETA DE CORES
# =============================================================================

CORES_PILOTO = {
    'norris': CORES['norris'],
    'piastri': CORES['piastri'],
    'verstappen': CORES['verstappen'],
}


# =============================================================================
# GRÁFICOS PRINCIPAIS
# =============================================================================

def grafico_barras_chances() -> go.Figure:
    """
    Gráfico de barras horizontais com chances de cada piloto.

    Returns:
        Figura Plotly
    """
    stats = carregar_estatisticas_resumo()
    df = stats['por_campeao'].copy()

    # Ordenar por chance
    df = df.sort_values('chance', ascending=True)
    df['piloto_label'] = df['campeao'].apply(label_piloto)
    df['cor'] = df['campeao'].map(CORES_PILOTO)

    fig = go.Figure()

    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row['chance']],
            y=[row['piloto_label']],
            orientation='h',
            marker_color=row['cor'],
            text=f"{row['chance']:.2f}%",
            textposition='outside',
            name=row['piloto_label'],
            hovertemplate=(
                f"<b>{row['piloto_label']}</b><br>"
                f"Chance: {row['chance']:.2f}%<br>"
                f"Combinações: {int(row['combinacoes']):,}<extra></extra>"
            ),
        ))

    fig.update_layout(
        title="Chances de Título por Piloto",
        xaxis_title="Chance (%)",
        yaxis_title="",
        showlegend=False,
        height=300,
        xaxis=dict(range=[0, 100]),
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig


def grafico_sunburst_metodo() -> go.Figure:
    """
    Gráfico sunburst mostrando campeão → método de decisão.

    Returns:
        Figura Plotly
    """
    stats = carregar_estatisticas_resumo()
    df = stats['campeao_metodo'].copy()

    # Preparar dados para sunburst
    labels = ['Total']
    parents = ['']
    values = [stats['total_combinacoes']]
    colors = ['#EEEEEE']

    # Adicionar campeões
    for campeao in df['campeao'].unique():
        df_c = df[df['campeao'] == campeao]
        total_c = df_c['combinacoes'].sum()
        labels.append(label_piloto(campeao))
        parents.append('Total')
        values.append(total_c)
        colors.append(CORES_PILOTO.get(campeao, '#888888'))

        # Adicionar métodos de cada campeão
        for _, row in df_c.iterrows():
            labels.append(f"{label_piloto(campeao)}\n{label_metodo(row['metodo_decisao'])}")
            parents.append(label_piloto(campeao))
            values.append(row['combinacoes'])
            colors.append(CORES_PILOTO.get(campeao, '#888888'))

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        marker=dict(colors=colors),
        hovertemplate='<b>%{label}</b><br>Combinações: %{value:,}<extra></extra>',
    ))

    fig.update_layout(
        title="Distribuição: Campeão → Método de Decisão",
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig


def grafico_metodos_decisao() -> go.Figure:
    """
    Gráfico de barras empilhadas mostrando métodos de decisão por campeão.

    Returns:
        Figura Plotly
    """
    stats = carregar_estatisticas_resumo()
    df = stats['campeao_metodo'].copy()

    # Pivotar para ter métodos como colunas
    df['piloto_label'] = df['campeao'].apply(label_piloto)
    df['metodo_label'] = df['metodo_decisao'].apply(label_metodo)

    # Cores para métodos
    metodos_unicos = df['metodo_decisao'].unique()
    cores_metodo = {
        'pontos': '#98D8C8',           # Verde menta
        'vitorias': '#F7DC6F',          # Amarelo
        'segundos_lugares': '#BB8FCE',  # Roxo claro
        'terceiros_lugares': '#85C1E9', # Azul claro
        'empate_total': '#F1948A',      # Vermelho claro
    }

    fig = go.Figure()

    for metodo in metodos_unicos:
        df_m = df[df['metodo_decisao'] == metodo]
        fig.add_trace(go.Bar(
            name=label_metodo(metodo),
            x=df_m['piloto_label'],
            y=df_m['pct'],
            marker_color=cores_metodo.get(metodo, '#888888'),
            hovertemplate=(
                f"<b>%{{x}}</b><br>"
                f"{label_metodo(metodo)}: %{{y:.2f}}%<extra></extra>"
            ),
        ))

    fig.update_layout(
        title="Como Cada Piloto Pode Ganhar (% por Método)",
        barmode='stack',
        xaxis_title="",
        yaxis_title="Chance (%)",
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=80, b=20),
    )

    return fig


def grafico_boxplot_pontos() -> go.Figure:
    """
    Boxplot mostrando distribuição de pontos finais por piloto.

    Returns:
        Figura Plotly
    """
    df = carregar_distribuicao_pontos()

    fig = go.Figure()

    for piloto, col in [
        ('norris', 'pts_final_norris'),
        ('piastri', 'pts_final_piastri'),
        ('verstappen', 'pts_final_verstappen'),
    ]:
        # Expandir considerando num_combinacoes (amostragem ponderada)
        # Para performance, usar quartis aproximados
        pontos = df[col].values
        pesos = df['num_combinacoes'].values

        fig.add_trace(go.Box(
            y=pontos,
            name=label_piloto(piloto),
            marker_color=CORES_PILOTO[piloto],
            boxpoints='outliers',
        ))

    fig.update_layout(
        title="Distribuição de Pontos Finais Possíveis",
        yaxis_title="Pontos",
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig


def grafico_comparativo_ranges() -> go.Figure:
    """
    Gráfico comparativo mostrando range de pontos de cada piloto.

    Returns:
        Figura Plotly
    """
    df = carregar_distribuicao_pontos()

    data = []
    for piloto, col in [
        ('norris', 'pts_final_norris'),
        ('piastri', 'pts_final_piastri'),
        ('verstappen', 'pts_final_verstappen'),
    ]:
        data.append({
            'piloto': label_piloto(piloto),
            'piloto_key': piloto,
            'min': df[col].min(),
            'max': df[col].max(),
            'media': (df[col] * df['num_combinacoes']).sum() / df['num_combinacoes'].sum(),
        })

    df_ranges = pd.DataFrame(data)

    fig = go.Figure()

    for _, row in df_ranges.iterrows():
        cor = CORES_PILOTO[row['piloto_key']]

        # Barra do range
        fig.add_trace(go.Bar(
            x=[row['max'] - row['min']],
            y=[row['piloto']],
            base=row['min'],
            orientation='h',
            marker_color=cor,
            opacity=0.6,
            name=row['piloto'],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['piloto']}</b><br>"
                f"Mínimo: {row['min']}<br>"
                f"Máximo: {row['max']}<br>"
                f"Média ponderada: {row['media']:.1f}<extra></extra>"
            ),
        ))

        # Marcador da média
        fig.add_trace(go.Scatter(
            x=[row['media']],
            y=[row['piloto']],
            mode='markers',
            marker=dict(size=15, color=cor, symbol='diamond'),
            showlegend=False,
            hoverinfo='skip',
        ))

    fig.update_layout(
        title="Range de Pontos Possíveis (◆ = média ponderada)",
        xaxis_title="Pontos",
        yaxis_title="",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig


def grafico_detalhamento_piloto(piloto: str, df_cenarios: pd.DataFrame) -> go.Figure:
    """
    Gráfico detalhado de cenários de vitória de um piloto específico.

    Args:
        piloto: Nome do piloto (lowercase)
        df_cenarios: DataFrame com cenários filtrados

    Returns:
        Figura Plotly
    """
    if df_cenarios.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum cenário encontrado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    # Agrupar por método
    df_metodo = df_cenarios.groupby('metodo_decisao').agg({
        'num_combinacoes': 'sum'
    }).reset_index()

    df_metodo['pct'] = 100 * df_metodo['num_combinacoes'] / df_metodo['num_combinacoes'].sum()
    df_metodo['metodo_label'] = df_metodo['metodo_decisao'].apply(label_metodo)

    cores_metodo = {
        'pontos': '#98D8C8',
        'vitorias': '#F7DC6F',
        'segundos_lugares': '#BB8FCE',
        'terceiros_lugares': '#85C1E9',
        'empate_total': '#F1948A',
    }
    df_metodo['cor'] = df_metodo['metodo_decisao'].map(cores_metodo)

    fig = go.Figure(go.Pie(
        labels=df_metodo['metodo_label'],
        values=df_metodo['num_combinacoes'],
        marker_colors=df_metodo['cor'],
        hovertemplate='<b>%{label}</b><br>%{value:,} combinações<br>%{percent}<extra></extra>',
        textinfo='percent+label',
    ))

    fig.update_layout(
        title=f"Como {label_piloto(piloto)} Pode Ganhar",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig


def grafico_delta_pontos_necessarios(piloto: str, df_cenarios: pd.DataFrame) -> go.Figure:
    """
    Histograma de delta de pontos necessários para vitória.

    Args:
        piloto: Nome do piloto
        df_cenarios: Cenários onde o piloto é campeão

    Returns:
        Figura Plotly
    """
    if df_cenarios.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum cenário encontrado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    col_delta = f'delta_pts_{piloto}'

    # Agregar por delta de pontos (soma ponderada por num_combinacoes)
    df_agg = df_cenarios.groupby(col_delta)['num_combinacoes'].sum().reset_index()
    df_agg = df_agg.sort_values(col_delta)

    fig = go.Figure(go.Bar(
        x=df_agg[col_delta],
        y=df_agg['num_combinacoes'],
        marker_color=CORES_PILOTO.get(piloto, '#888888'),
        hovertemplate='Delta pontos: %{x}<br>Combinações: %{y:,}<extra></extra>',
    ))

    fig.update_layout(
        title=f"Distribuição de Pontos Ganhos - {label_piloto(piloto)}",
        xaxis_title="Pontos Ganhos nas Corridas Restantes",
        yaxis_title="Combinações",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        bargap=0.1,
    )

    return fig
