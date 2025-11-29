"""
Funções utilitárias de formatação.
"""


def formatar_posicao(pos: int) -> str:
    """
    Formata posição para exibição.
    99 representa 'fora dos pontos' e é exibido como 'Fora'.

    Args:
        pos: Posição numérica (1-10 ou 99)

    Returns:
        String formatada (ex: '1º', '2º', 'Fora')
    """
    return 'Fora' if pos == 99 else f'{pos}º'


def formatar_pontos(pts: int) -> str:
    """
    Formata pontuação para exibição.

    Args:
        pts: Pontuação numérica

    Returns:
        String formatada (ex: '390 pts')
    """
    return f'{pts} pts'
