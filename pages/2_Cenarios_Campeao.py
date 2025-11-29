"""
Página de Cenários de Campeão F1 2025.
Análise de todas as combinações possíveis de resultados e chances de título.
"""

import streamlit as st
import pandas as pd

from config.settings import PILOTOS, CORES
from components.driver_card import cards_pilotos
from simulations.cenarios_campeao.filters import (
    carregar_estatisticas_resumo,
    carregar_cenarios_vitoria,
    carregar_opcoes_filtros,
    metricas_resumo,
    cards_chances,
    label_piloto,
    label_metodo,
    label_posicao,
    LABELS_PILOTO,
)
from simulations.cenarios_campeao.charts import (
    grafico_barras_chances,
    grafico_sunburst_metodo,
    grafico_metodos_decisao,
    grafico_boxplot_pontos,
    grafico_comparativo_ranges,
    grafico_detalhamento_piloto,
    grafico_delta_pontos_necessarios,
)
from simulations.cenarios_campeao.simulator import (
    determinar_campeao,
    PONTOS_ATUAIS,
    VITORIAS_ATUAIS,
    SEGUNDOS_ATUAIS,
    TERCEIROS_ATUAIS,
    FORA_PONTOS,
)
from config.settings import PONTOS_SPRINT, PONTOS_CORRIDA


# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Cenários de Campeão | F1 2025",
    page_icon="🏆",
    layout="wide",
)

# CSS customizado
st.markdown("""
<style>
    .stMetric {
        background: #F5F5F5;
        padding: 15px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def calcular_resultado_simulador(
    sprint_norris: int, sprint_piastri: int, sprint_verstappen: int,
    qatar_norris: int, qatar_piastri: int, qatar_verstappen: int,
    abudhabi_norris: int, abudhabi_piastri: int, abudhabi_verstappen: int,
) -> tuple[str, str, dict]:
    """
    Calcula o resultado do simulador interativo.

    Returns:
        (campeao, metodo, stats_finais)
    """
    # Calcular deltas de pontos
    def pts_sprint(pos): return PONTOS_SPRINT.get(pos, 0)
    def pts_race(pos): return PONTOS_CORRIDA.get(pos, 0)
    def is_vitoria(pos): return 1 if pos == 1 else 0
    def is_segundo(pos): return 1 if pos == 2 else 0
    def is_terceiro(pos): return 1 if pos == 3 else 0

    # Pontos ganhos
    pts_norris = pts_sprint(sprint_norris) + pts_race(qatar_norris) + pts_race(abudhabi_norris)
    pts_piastri = pts_sprint(sprint_piastri) + pts_race(qatar_piastri) + pts_race(abudhabi_piastri)
    pts_verstappen = pts_sprint(sprint_verstappen) + pts_race(qatar_verstappen) + pts_race(abudhabi_verstappen)

    # Vitórias ganhas
    wins_norris = is_vitoria(sprint_norris) + is_vitoria(qatar_norris) + is_vitoria(abudhabi_norris)
    wins_piastri = is_vitoria(sprint_piastri) + is_vitoria(qatar_piastri) + is_vitoria(abudhabi_piastri)
    wins_verstappen = is_vitoria(sprint_verstappen) + is_vitoria(qatar_verstappen) + is_vitoria(abudhabi_verstappen)

    # Segundos
    sec_norris = is_segundo(sprint_norris) + is_segundo(qatar_norris) + is_segundo(abudhabi_norris)
    sec_piastri = is_segundo(sprint_piastri) + is_segundo(qatar_piastri) + is_segundo(abudhabi_piastri)
    sec_verstappen = is_segundo(sprint_verstappen) + is_segundo(qatar_verstappen) + is_segundo(abudhabi_verstappen)

    # Terceiros
    thi_norris = is_terceiro(sprint_norris) + is_terceiro(qatar_norris) + is_terceiro(abudhabi_norris)
    thi_piastri = is_terceiro(sprint_piastri) + is_terceiro(qatar_piastri) + is_terceiro(abudhabi_piastri)
    thi_verstappen = is_terceiro(sprint_verstappen) + is_terceiro(qatar_verstappen) + is_terceiro(abudhabi_verstappen)

    # Stats finais
    pts_final = (
        PONTOS_ATUAIS['norris'] + pts_norris,
        PONTOS_ATUAIS['piastri'] + pts_piastri,
        PONTOS_ATUAIS['verstappen'] + pts_verstappen,
    )
    wins_final = (
        VITORIAS_ATUAIS['norris'] + wins_norris,
        VITORIAS_ATUAIS['piastri'] + wins_piastri,
        VITORIAS_ATUAIS['verstappen'] + wins_verstappen,
    )
    sec_final = (
        SEGUNDOS_ATUAIS['norris'] + sec_norris,
        SEGUNDOS_ATUAIS['piastri'] + sec_piastri,
        SEGUNDOS_ATUAIS['verstappen'] + sec_verstappen,
    )
    thi_final = (
        TERCEIROS_ATUAIS['norris'] + thi_norris,
        TERCEIROS_ATUAIS['piastri'] + thi_piastri,
        TERCEIROS_ATUAIS['verstappen'] + thi_verstappen,
    )

    campeao, metodo = determinar_campeao(pts_final, wins_final, sec_final, thi_final)

    stats = {
        'norris': {'pts': pts_final[0], 'wins': wins_final[0], 'delta_pts': pts_norris},
        'piastri': {'pts': pts_final[1], 'wins': wins_final[1], 'delta_pts': pts_piastri},
        'verstappen': {'pts': pts_final[2], 'wins': wins_final[2], 'delta_pts': pts_verstappen},
    }

    return campeao, metodo, stats


# =============================================================================
# TABS
# =============================================================================

def tab_como_ganhar():
    """Tab: Como Cada Um Pode Ganhar."""
    st.header("🎯 Como Cada Piloto Pode Ganhar")

    st.markdown("""
    Análise detalhada das combinações de resultados que levam cada piloto ao título.
    """)

    # Gráfico principal de chances
    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(grafico_barras_chances(), use_container_width=True)

    with col2:
        st.plotly_chart(grafico_metodos_decisao(), use_container_width=True)

    st.markdown("---")

    # Sunburst
    st.subheader("Hierarquia: Campeão → Método de Decisão")
    st.plotly_chart(grafico_sunburst_metodo(), use_container_width=True)

    st.markdown("---")

    # Detalhamento por piloto
    st.subheader("📊 Detalhamento por Piloto")

    piloto_selecionado = st.selectbox(
        "Selecione o piloto para ver detalhes:",
        options=['norris', 'piastri', 'verstappen'],
        format_func=label_piloto,
        key='piloto_detalhe'
    )

    df_cenarios = carregar_cenarios_vitoria(piloto_selecionado)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            grafico_detalhamento_piloto(piloto_selecionado, df_cenarios),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            grafico_delta_pontos_necessarios(piloto_selecionado, df_cenarios),
            use_container_width=True
        )

    # Estatísticas do piloto
    if not df_cenarios.empty:
        col_pts = f'delta_pts_{piloto_selecionado}'

        stats_piloto = {
            'min_pts': df_cenarios[col_pts].min(),
            'max_pts': df_cenarios[col_pts].max(),
            'total_comb': df_cenarios['num_combinacoes'].sum(),
        }

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Mínimo de Pontos Necessários", stats_piloto['min_pts'])
        with c2:
            st.metric("Máximo de Pontos Possíveis", stats_piloto['max_pts'])
        with c3:
            st.metric("Total de Combinações Vitoriosas", f"{stats_piloto['total_comb']:,}".replace(',', '.'))


def tab_simulador():
    """Tab: Simulador E Se?"""
    st.header("🎮 Simulador 'E Se?'")

    st.markdown("""
    Selecione os resultados de cada piloto em cada corrida restante e veja quem seria o campeão.
    """)

    # Opções de posição
    posicoes_sprint = [1, 2, 3, 4, 5, 6, 7, 8, 99]
    posicoes_race = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 99]

    def format_posicao(p):
        return label_posicao(p)

    st.subheader("🏁 Sprint Qatar")
    col1, col2, col3 = st.columns(3)

    with col1:
        sprint_norris = st.selectbox(
            f"🟠 {label_piloto('norris')}",
            posicoes_sprint,
            format_func=format_posicao,
            key='sprint_norris',
            index=0
        )
    with col2:
        sprint_piastri = st.selectbox(
            f"🔵 {label_piloto('piastri')}",
            posicoes_sprint,
            format_func=format_posicao,
            key='sprint_piastri',
            index=1
        )
    with col3:
        sprint_verstappen = st.selectbox(
            f"🟣 {label_piloto('verstappen')}",
            posicoes_sprint,
            format_func=format_posicao,
            key='sprint_verstappen',
            index=2
        )

    st.subheader("🏎️ GP Qatar (Corrida)")
    col1, col2, col3 = st.columns(3)

    with col1:
        qatar_norris = st.selectbox(
            f"🟠 {label_piloto('norris')}",
            posicoes_race,
            format_func=format_posicao,
            key='qatar_norris',
            index=0
        )
    with col2:
        qatar_piastri = st.selectbox(
            f"🔵 {label_piloto('piastri')}",
            posicoes_race,
            format_func=format_posicao,
            key='qatar_piastri',
            index=1
        )
    with col3:
        qatar_verstappen = st.selectbox(
            f"🟣 {label_piloto('verstappen')}",
            posicoes_race,
            format_func=format_posicao,
            key='qatar_verstappen',
            index=2
        )

    st.subheader("🏎️ GP Abu Dhabi (Corrida)")
    col1, col2, col3 = st.columns(3)

    with col1:
        abudhabi_norris = st.selectbox(
            f"🟠 {label_piloto('norris')}",
            posicoes_race,
            format_func=format_posicao,
            key='abudhabi_norris',
            index=0
        )
    with col2:
        abudhabi_piastri = st.selectbox(
            f"🔵 {label_piloto('piastri')}",
            posicoes_race,
            format_func=format_posicao,
            key='abudhabi_piastri',
            index=1
        )
    with col3:
        abudhabi_verstappen = st.selectbox(
            f"🟣 {label_piloto('verstappen')}",
            posicoes_race,
            format_func=format_posicao,
            key='abudhabi_verstappen',
            index=2
        )

    st.markdown("---")

    # Calcular resultado
    campeao, metodo, stats = calcular_resultado_simulador(
        sprint_norris, sprint_piastri, sprint_verstappen,
        qatar_norris, qatar_piastri, qatar_verstappen,
        abudhabi_norris, abudhabi_piastri, abudhabi_verstappen,
    )

    # Exibir resultado
    st.subheader("🏆 Resultado")

    cor_campeao = {
        'norris': CORES['norris'],
        'piastri': CORES['piastri'],
        'verstappen': CORES['verstappen'],
    }

    st.markdown(f"""
    <div style="
        background: {cor_campeao[campeao]}40;
        padding: 30px;
        border-radius: 15px;
        border-left: 8px solid {cor_campeao[campeao]};
        text-align: center;
        margin: 20px 0;
    ">
        <h1 style="margin: 0; color: #4A4A4A;">🏆 {label_piloto(campeao)}</h1>
        <p style="font-size: 20px; color: #666; margin: 10px 0;">
            Campeão Mundial F1 2025
        </p>
        <p style="font-size: 16px; color: #888;">
            Decidido por: <strong>{label_metodo(metodo)}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Tabela de pontuação final
    st.subheader("📊 Classificação Final")

    # Ordenar por pontos
    classificacao = sorted(
        stats.items(),
        key=lambda x: (x[1]['pts'], x[1]['wins']),
        reverse=True
    )

    cols = st.columns(3)
    for i, (piloto, s) in enumerate(classificacao):
        with cols[i]:
            pos_emoji = ['🥇', '🥈', '🥉'][i]
            st.markdown(f"""
            <div style="
                background: {cor_campeao[piloto]}30;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            ">
                <h3 style="margin: 0;">{pos_emoji} {label_piloto(piloto)}</h3>
                <p style="font-size: 28px; font-weight: bold; margin: 10px 0;">{s['pts']} pts</p>
                <p style="font-size: 14px; color: #666;">
                    {s['wins']} vitórias<br>
                    <span style="color: green;">+{s['delta_pts']} pts ganhos</span>
                </p>
            </div>
            """, unsafe_allow_html=True)


def tab_comparativo():
    """Tab: Comparativo lado a lado."""
    st.header("📊 Comparativo entre Pilotos")

    st.markdown("""
    Comparação detalhada das chances e requisitos de cada piloto para o título.
    """)

    stats = carregar_estatisticas_resumo()

    # Gráfico de ranges
    st.plotly_chart(grafico_comparativo_ranges(), use_container_width=True)

    st.markdown("---")

    # Boxplot
    st.subheader("Distribuição de Pontos Finais")
    st.plotly_chart(grafico_boxplot_pontos(), use_container_width=True)

    st.markdown("---")

    # Tabela comparativa
    st.subheader("📋 Resumo Comparativo")

    # Carregar dados para cada piloto
    df_campeao = stats['por_campeao']
    df_metodo = stats['campeao_metodo']

    cols = st.columns(3)
    pilotos_ordem = ['norris', 'piastri', 'verstappen']

    for i, piloto in enumerate(pilotos_ordem):
        with cols[i]:
            cor = CORES[piloto]

            # Dados do piloto
            row = df_campeao[df_campeao['campeao'] == piloto]
            if not row.empty:
                chance = row.iloc[0]['chance']
                combinacoes = int(row.iloc[0]['combinacoes'])
            else:
                chance = 0
                combinacoes = 0

            # Métodos desse piloto
            df_metodos_piloto = df_metodo[df_metodo['campeao'] == piloto]

            st.markdown(f"""
            <div style="
                background: {cor}30;
                padding: 20px;
                border-radius: 10px;
                border-top: 4px solid {cor};
            ">
                <h2 style="margin: 0; text-align: center; color: #4A4A4A;">
                    {label_piloto(piloto)}
                </h2>
                <p style="font-size: 36px; font-weight: bold; text-align: center; color: {cor}; margin: 15px 0;">
                    {chance:.2f}%
                </p>
                <p style="text-align: center; color: #666; font-size: 14px;">
                    {combinacoes:,} combinações vitoriosas
                </p>
            </div>
            """.replace(',', '.'), unsafe_allow_html=True)

            st.markdown("**Como pode ganhar:**")
            for _, m in df_metodos_piloto.iterrows():
                st.markdown(f"- {label_metodo(m['metodo_decisao'])}: {m['pct']:.2f}%")

            # Stats adicionais
            df_cenarios = carregar_cenarios_vitoria(piloto)
            if not df_cenarios.empty:
                col_pts = f'delta_pts_{piloto}'
                st.markdown(f"""
                **Pontos necessários:**
                - Mínimo: {df_cenarios[col_pts].min()}
                - Máximo: {df_cenarios[col_pts].max()}
                """)


# =============================================================================
# MAIN
# =============================================================================

def main():
    st.title("🏆 Cenários de Campeão F1 2025")
    st.markdown("---")

    # Cards de pilotos
    cards_pilotos(PILOTOS)

    st.markdown("---")

    # Métricas resumo
    metricas_resumo()

    st.markdown("---")

    # Cards de chances
    st.subheader("📊 Chances de Título")
    cards_chances()

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 Como Cada Um Ganha",
        "🎮 Simulador 'E Se?'",
        "📊 Comparativo",
    ])

    with tab1:
        tab_como_ganhar()

    with tab2:
        tab_simulador()

    with tab3:
        tab_comparativo()

    # Footer
    st.markdown("---")
    st.caption("🏁 Simulador F1 2025 | Desenvolvido com Streamlit & Plotly")


if __name__ == '__main__':
    main()
