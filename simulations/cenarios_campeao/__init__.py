"""
Módulo de simulação: Cenários de Campeão F1 2025.

Calcula todas as combinações possíveis de resultados nas corridas restantes
para determinar cenários de campeonato entre Norris, Piastri e Verstappen.
"""

from .simulator import (
    executar,
    simular_cenarios,
    gerar_estatisticas,
    imprimir_estatisticas,
    criar_tabela,
    PONTOS_ATUAIS,
    VITORIAS_ATUAIS,
)

__all__ = [
    'executar',
    'simular_cenarios',
    'gerar_estatisticas',
    'imprimir_estatisticas',
    'criar_tabela',
    'PONTOS_ATUAIS',
    'VITORIAS_ATUAIS',
]
