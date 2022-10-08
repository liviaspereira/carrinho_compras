class ObjetoNaoEncontrado(Exception):
    """Quando for feito uma update e o matched_count == 0"""


class ObjetoNaoModificado(Exception):
    """Quando o update for igual a um existente"""
