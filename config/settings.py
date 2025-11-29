"""
Configurações globais do projeto F1 2025 Simulations.
Paleta de cores, dados dos pilotos e tabelas de pontuação.
"""

from pathlib import Path

# =============================================================================
# CAMINHOS BASE
# =============================================================================

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent.parent

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

# =============================================================================
# DADOS DOS PILOTOS
# =============================================================================

PILOTOS = {
    'Norris': {
        'pontos_iniciais': 390,
        'foto': str(ROOT_DIR / 'assets' / 'norris.png'),
        'cor': CORES['norris']
    },
    'Piastri': {
        'pontos_iniciais': 366,
        'foto': str(ROOT_DIR / 'assets' / 'piastri.png'),
        'cor': CORES['piastri']
    },
    'Verstappen': {
        'pontos_iniciais': 366,
        'foto': str(ROOT_DIR / 'assets' / 'verstappen.png'),
        'cor': CORES['verstappen']
    },
}

# Versão simplificada para o simulador (chaves em minúsculo)
PILOTOS_SIMULADOR = {
    'norris': {'nome': 'L. Norris', 'pontos': 390},
    'piastri': {'nome': 'O. Piastri', 'pontos': 366},
    'verstappen': {'nome': 'M. Verstappen', 'pontos': 366},
}

# =============================================================================
# TABELAS DE PONTUAÇÃO F1
# =============================================================================

# Pontos por posição na Sprint (top 8 pontuam)
PONTOS_SPRINT = {
    1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1,
    99: 0  # Fora dos pontos
}

# Pontos por posição na Corrida (top 10 pontuam)
PONTOS_CORRIDA = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1,
    99: 0  # Fora dos pontos
}

# Posições possíveis
POSICOES_SPRINT = [1, 2, 3, 4, 5, 6, 7, 8, 99]
POSICOES_CORRIDA = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 99]
