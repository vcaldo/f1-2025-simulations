"""
Componente de card de piloto.
Exibe foto, nome e pontuação de um piloto.
"""

import streamlit as st
from pathlib import Path
from config.settings import CORES


def card_piloto(nome: str, dados: dict, col):
    """
    Renderiza card de piloto com foto e informações.

    Args:
        nome: Nome do piloto
        dados: Dicionário com 'pontos_iniciais', 'foto', 'cor'
        col: Coluna do Streamlit onde renderizar
    """
    with col:
        # Foto do piloto
        foto_path = Path(dados['foto'])
        if foto_path.exists():
            st.image(str(foto_path), width=150)

        # Nome e pontos com estilo
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
        </div>
        """, unsafe_allow_html=True)


def cards_pilotos(pilotos: dict):
    """
    Renderiza cards de todos os pilotos em colunas.

    Args:
        pilotos: Dicionário de pilotos (nome -> dados)
    """
    cols = st.columns(len(pilotos))
    for i, (nome, dados) in enumerate(pilotos.items()):
        card_piloto(nome, dados, cols[i])
