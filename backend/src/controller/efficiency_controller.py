""" Módulo de controle para eficiência do banco de dados local """

import pandas as pd

# pylint: disable=import-error
from src.service.efficiency_service import EfficiencyService


class EfficiencyController:
    """Classe para controle dos dados do banco de dados local de eficiência."""

    def __init__(self) -> None:
        self.__efficiency_service = EfficiencyService()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de eficiência."""
        return self.__efficiency_service.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de eficiência."""
        self.__efficiency_service.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de eficiência."""
        self.__efficiency_service.replace_data(data)
