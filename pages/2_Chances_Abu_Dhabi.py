"""
Dashboard: Chances de Título - Abu Dhabi (Última Etapa)
Simule as probabilidades de cada piloto conquistar o campeonato.

🚧 Em construção
"""

import streamlit as st

from config.settings import PILOTOS
from components.driver_card import cards_pilotos

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Chances de Título - Abu Dhabi | F1 2025",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================

def main():
    # Header
    st.title("🏆 Chances de Título - Abu Dhabi")
    st.markdown("Simule as probabilidades de cada piloto conquistar o campeonato na última corrida em Abu Dhabi.")

    st.markdown("---")

    # Cards dos pilotos
    st.markdown("### 🏆 Classificação Atual - Candidatos ao Título")
    cards_pilotos(PILOTOS)

    st.markdown("---")

    # Placeholder - Em construção
    st.info("🚧 **Esta simulação está em construção.**")

    st.markdown("""
    ### O que será possível fazer aqui:

    - 📊 Simular diferentes resultados na última corrida
    - 🎲 Calcular probabilidades de cada piloto ser campeão
    - 🔄 Analisar cenários de desempate
    - 📈 Visualizar todas as combinações possíveis de resultado final

    ---

    *Volte em breve para conferir as atualizações!*
    """)

    # Footer
    st.markdown("---")
    st.caption("🏁 Simulador F1 2025 | Desenvolvido com Streamlit & Plotly")


if __name__ == '__main__':
    main()
