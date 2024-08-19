""" Módulo com variáveis e tipos auxiliares para o projeto. """

from enum import Enum


class IndicatorType(Enum):
    """
    Enum para os tipos de indicadores.
    """

    EFFICIENCY = "eficiencia"
    PERFORMANCE = "performance"
    REPAIR = "reparo"
