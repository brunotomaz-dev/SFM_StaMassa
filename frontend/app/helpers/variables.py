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

class BSColorsEnum(Enum):
    """Bootstrap colors"""

    PRIMARY_COLOR = "#0d6efd"
    SECONDARY_COLOR = "#6c757d"
    SUCCESS_COLOR = "#00A13A"
    WARNING_COLOR = "#ffc107"
    DANGER_COLOR = "#E30613"
    INFO_COLOR = "#0dcaf0"
    TEAL_COLOR = "#20c997"
    INDIGO_COLOR = "#6610f2"
    GRAY_COLOR = "#adb5bd"
    GREY_400_COLOR = "#ced4da"
    GREY_500_COLOR = "#adb5bd"
    GREY_600_COLOR = "#6c757d"
    GREY_700_COLOR = "#495057"
    GREY_800_COLOR = "#343a40"
    GREY_900_COLOR = "#212529"
    ORANGE_COLOR = "#fd7e14"
    PINK_COLOR = "#d63384"
    PURPLE_COLOR = "#6f42c1"
    SPACE_CADET_COLOR = "#282f44"
    BLUE_DELFT_COLOR = "#353e5a"


COLOR_DICT = {
    "Não apontado": BSColorsEnum.WARNING_COLOR.value,
    "Ajustes": BSColorsEnum.PRIMARY_COLOR.value,
    "Manutenção": BSColorsEnum.SPACE_CADET_COLOR.value,
    "Qualidade": BSColorsEnum.INFO_COLOR.value,
    "Fluxo": BSColorsEnum.PINK_COLOR.value,
    "Parada Programada": BSColorsEnum.DANGER_COLOR.value,
    "Setup": BSColorsEnum.BLUE_DELFT_COLOR.value,
    "Saída para Backup": BSColorsEnum.TEAL_COLOR.value,
    "Limpeza": BSColorsEnum.ORANGE_COLOR.value,
    "Rodando": BSColorsEnum.SUCCESS_COLOR.value,
    "Liberada": BSColorsEnum.GREY_500_COLOR.value,
}

MANUT_COLORS = {
    "Termoformadora": BSColorsEnum.INFO_COLOR.value,
    "Recheadora": BSColorsEnum.PINK_COLOR.value,
    "Robô": BSColorsEnum.GREY_500_COLOR.value,
    "Armadora de Caixas": BSColorsEnum.INDIGO_COLOR.value,
    "Seladora de Caixas": BSColorsEnum.PURPLE_COLOR.value,
    "Detector de Metais": BSColorsEnum.ORANGE_COLOR.value,
}
