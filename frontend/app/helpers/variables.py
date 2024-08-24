""" Módulo com variáveis e tipos auxiliares para o projeto. """

from enum import Enum


class IndicatorType(Enum):
    """
    Enum para os tipos de indicadores.
    """

    EFFICIENCY = "eficiencia"
    PERFORMANCE = "performance"
    REPAIR = "reparo"


class ColorsSTM(Enum):
    """Enum de cores do padrão Santa Massa."""

    RED = "#E30613"
    LIGHT_GREY = "#E3E3E3"
    YELLOW = "#FFDD00"
    GREEN = "#00A13A"


TURNOS = ["NOT", "MAT", "VES"]
