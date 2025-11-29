"""
Dashboard F1 2025 - Simulações
Página inicial com visão geral e navegação para simulações disponíveis.
"""

import streamlit as st

from config.settings import PILOTOS
from components.driver_card import cards_pilotos

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Simulações F1 2025",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================

def main():
    # Header
    st.title("🏎️ Simulações F1 2025")
    st.warning("⚠️ Válido Apenas para o dia 29 de Novembro de 2025, antes da Sprint Race")
    st.markdown("Dashboard interativo para simulações do campeonato de Fórmula 1 2025.")

    st.markdown("---")

    # Cards dos pilotos - Classificação atual
    st.markdown("### 🏆 Classificação Atual - Candidatos ao Título")
    cards_pilotos(PILOTOS)

    st.markdown("---")

    # Informações sobre as simulações disponíveis
    st.markdown("### 📊 Simulações Disponíveis")
    st.markdown("Use o menu lateral para navegar entre as simulações:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🏁 Cenários de Empate para Última Etapa
        st.warning("⚠️ Válido Apenas para o dia 29 de Novembro de 2025, antes da Sprint Race")
        Visualize todos os cenários onde 2 ou 3 pilotos podem empatar
        na liderança antes da última etapa.

        """)

    with col2:
        st.markdown("""
        #### 🏆 Cenários de Campeão
        Simule as probabilidades de cada piloto conquistar o
        campeonato na última corrida.

        """)

    # Footer
    st.markdown("---")
    st.caption("🏁 Simulador F1 2025 | Desenvolvido com Streamlit & Plotly")


if __name__ == '__main__':
    main()
