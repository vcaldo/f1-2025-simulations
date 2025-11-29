"""
Dashboard: Cenários de Empate - Qatar (Penúltima Etapa)
Visualização interativa dos cenários onde 2 ou 3 pilotos empatam na liderança.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from config.settings import PILOTOS
from components.driver_card import cards_pilotos
from simulations.cenarios_empate.charts import (
    grafico_barras_combinacoes,
    grafico_sunburst,
    grafico_heatmap_posicoes,
    grafico_pontos_ganhos
)
from simulations.cenarios_empate.filters import sidebar_filtros, metricas_resumo

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Cenários de Empate - Qatar | F1 2025",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CARREGAMENTO DE DADOS
# =============================================================================

@st.cache_data
def carregar_dados():
    """Carrega e processa o CSV de cenários."""
    csv_path = Path(__file__).parent.parent / 'simulations' / 'cenarios_empate' / 'data' / 'cenarios_empate.csv'
    df = pd.read_csv(csv_path)
    return df

# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================

def main():
    # Header
    st.title("🏁 Cenários de Empate - Qatar")
    st.markdown("Visualize todos os cenários onde 2 ou 3 pilotos podem empatar na liderança após a penúltima etapa (Qatar).")

    st.markdown("---")

    # Carregar dados
    df = carregar_dados()

    # Cards dos pilotos
    st.markdown("### 🏆 Classificação Atual - Candidatos ao Título")
    cards_pilotos(PILOTOS)

    st.markdown("---")

    # Aplicar filtros (sidebar)
    df_filtrado = sidebar_filtros(df)

    # Métricas resumo
    st.markdown("### 📊 Resumo dos Cenários")
    metricas_resumo(df_filtrado, df)

    st.markdown("---")

    # Visualizações em tabs
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
            st.warning("Dados de pontos ganhos não disponíveis. Regenere o CSV executando o simulador.")

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
    st.caption("🏁 Simulador F1 2025 | Desenvolvido com Streamlit & Plotly")


if __name__ == '__main__':
    main()
