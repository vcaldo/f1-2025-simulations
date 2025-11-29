"""
Dashboard F1 2025 - Cenários de Empate
Visualização interativa dos cenários onde 2 ou 3 pilotos empatam na liderança.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="F1 2025 - Cenários de Empate",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# PALETA DE CORES PASTÉIS
# =============================================================================

CORES = {
    'norris': '#FFB347',      # Pêssego/Laranja pastel (McLaren)
    'piastri': '#87CEEB',     # Azul céu pastel
    'verstappen': '#DDA0DD',  # Lavanda pastel
    'fundo': '#F5F5F5',
    'texto': '#4A4A4A',
    'destaque': '#98D8C8',    # Verde menta pastel
    'grafico': ['#FFB347', '#87CEEB', '#DDA0DD', '#98D8C8', '#F7DC6F', '#C39BD3']
}

# Dados dos pilotos
PILOTOS = {
    'Norris': {'pontos_iniciais': 390, 'foto': 'assets/norris.png', 'cor': CORES['norris']},
    'Piastri': {'pontos_iniciais': 366, 'foto': 'assets/piastri.png', 'cor': CORES['piastri']},
    'Verstappen': {'pontos_iniciais': 366, 'foto': 'assets/verstappen.png', 'cor': CORES['verstappen']},
}

# =============================================================================
# FUNÇÕES DE CARREGAMENTO
# =============================================================================

@st.cache_data
def carregar_dados():
    """Carrega e processa o CSV de cenários."""
    df = pd.read_csv('cenarios_empate.csv')
    return df


def formatar_posicao(pos):
    """Formata posição para exibição (99 -> 'Fora')."""
    return 'Fora' if pos == 99 else f'{pos}º'

# =============================================================================
# COMPONENTES VISUAIS
# =============================================================================

def card_piloto(nome, dados, col):
    """Renderiza card de piloto com foto e informações."""
    with col:
        # Foto do piloto
        foto_path = Path(dados['foto'])
        if foto_path.exists():
            st.image(str(foto_path), width=150)

        # Nome e pontos
        st.markdown(f"""
        <div style="
            background: {dados['cor']}40;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {dados['cor']};
            text-align: center;
        ">
            <h3 style="margin: 0; color: {CORES['texto']};">{nome}</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 5px 0; color: {CORES['texto']};">
                {dados['pontos_iniciais']} pts
            </p>
            <p style="font-size: 12px; color: #888; margin: 0;">Pontos atuais</p>
        </div>
        """, unsafe_allow_html=True)


def metricas_resumo(df_filtrado, df_total):
    """Exibe métricas resumo dos cenários filtrados."""
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

# =============================================================================
# VISUALIZAÇÕES
# =============================================================================

def grafico_barras_combinacoes(df):
    """Gráfico de barras com contagem por combinação de pilotos."""
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


def grafico_sunburst(df):
    """Gráfico sunburst hierárquico: tipo -> pilotos -> faixa de pontos."""
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


def grafico_heatmap_posicoes(df, piloto):
    """Heatmap de frequência sprint x corrida para um piloto."""
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


def grafico_pontos_ganhos(df):
    """Gráfico de dispersão: pontos ganhos por cada piloto."""
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

# =============================================================================
# SIDEBAR - FILTROS
# =============================================================================

def sidebar_filtros(df):
    """Cria filtros na sidebar e retorna DataFrame filtrado."""
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

# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================

def main():
    # Header
    st.title("🏎️ F1 2025 - Simulador de Cenários de Empate")
    st.markdown("Visualização dos cenários onde 2 ou 3 pilotos terminam empatados após a penúltima etapa.")

    # Carregar dados
    df = carregar_dados()

    # Cards dos pilotos
    st.markdown("### 👤 Classificação Atual")
    cols = st.columns(3)
    for i, (nome, dados) in enumerate(PILOTOS.items()):
        card_piloto(nome, dados, cols[i])

    st.markdown("---")

    # Aplicar filtros
    df_filtrado = sidebar_filtros(df)

    # Métricas resumo
    st.markdown("### 📊 Resumo dos Cenários")
    metricas_resumo(df_filtrado, df)

    st.markdown("---")

    # Visualizações
    st.markdown("### 📈 Visualizações")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Por Combinação",
        "🎯 Hierarquia",
        "🔥 Heatmaps",
        "📦 Pontos Ganhos"
    ])

    with tab1:
        if len(df_filtrado) > 0:
            st.plotly_chart(grafico_barras_combinacoes(df_filtrado), use_container_width=True)
        else:
            st.warning("Nenhum cenário encontrado com os filtros selecionados.")

    with tab2:
        if len(df_filtrado) > 0:
            st.plotly_chart(grafico_sunburst(df_filtrado), use_container_width=True)
        else:
            st.warning("Nenhum cenário encontrado com os filtros selecionados.")

    with tab3:
        if len(df_filtrado) > 0:
            piloto_heatmap = st.selectbox(
                "Selecione o piloto:",
                list(PILOTOS.keys()),
                key="heatmap_piloto"
            )
            st.plotly_chart(grafico_heatmap_posicoes(df_filtrado, piloto_heatmap), use_container_width=True)
        else:
            st.warning("Nenhum cenário encontrado com os filtros selecionados.")

    with tab4:
        if len(df_filtrado) > 0 and 'ganhos_norris' in df_filtrado.columns:
            st.plotly_chart(grafico_pontos_ganhos(df_filtrado), use_container_width=True)
        else:
            st.warning("Dados de pontos ganhos não disponíveis. Regenere o CSV executando f1_simulator.py.")

    st.markdown("---")

    # Tabela de cenários
    st.markdown("### 📋 Tabela de Cenários")

    # Configurar colunas para exibição
    colunas_exibir = [
        'tipo_empate', 'pilotos_empatados', 'pontos_empate',
        'sprint_norris', 'corrida_norris', 'pts_norris',
        'sprint_piastri', 'corrida_piastri', 'pts_piastri',
        'sprint_verstappen', 'corrida_verstappen', 'pts_verstappen'
    ]

    colunas_disponiveis = [c for c in colunas_exibir if c in df_filtrado.columns]

    st.dataframe(
        df_filtrado[colunas_disponiveis].head(100),
        use_container_width=True,
        hide_index=True
    )

    if len(df_filtrado) > 100:
        st.caption(f"Exibindo 100 de {len(df_filtrado)} cenários. Use os filtros para refinar.")

    # Footer
    st.markdown("---")
    st.caption("🏁 Simulador F1 2025 | Dados gerados por f1_simulator.py")


if __name__ == '__main__':
    main()
