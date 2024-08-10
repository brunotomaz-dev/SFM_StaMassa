""" Módulo com as variáveis do sistema e classes auxiliares. """

from enum import Enum

# cSpell: words eficiencia, manutencao


class IndicatorType(Enum):
    """
    Enum para os tipos de indicadores.
    """

    EFFICIENCY = "eficiencia"
    PERFORMANCE = "performance"
    REPAIR = "reparo"
    QUALITY = "qualidade"
    MAINTENANCE = "manutencao"
