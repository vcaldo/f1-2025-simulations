"""
Componente de card de piloto.
Exibe foto, nome e pontuação de um piloto.
"""

import streamlit as st
from pathlib import Path
from config.settings import CORES
import base64


def card_piloto(nome: str, dados: dict, col):
    """
    Renderiza card de piloto com foto e informações em layout horizontal.

    Args:
        nome: Nome do piloto
        dados: Dicionário com 'pontos_iniciais', 'foto', 'cor'
        col: Coluna do Streamlit onde renderizar
    """
    with col:
        # Carregar e codificar imagem em base64
        foto_path = Path(dados['foto'])
        img_base64 = ""
        if foto_path.exists():
            with open(foto_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()

        # Card com layout horizontal (foto à esquerda, info à direita)
        st.markdown(f"""
        <div style="
            background: {dados['cor']}40;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {dados['cor']};
            display: flex;
            align-items: center;
            gap: 15px;
        ">
            <img src="data:image/avif;base64,{img_base64}"
                 style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px; flex-shrink: 0;">
            <div style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: {CORES['texto']};">{nome}</h3>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0; color: {CORES['texto']};">
                    {dados['pontos_iniciais']} pts
                </p>
            </div>
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
