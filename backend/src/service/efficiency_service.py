"""Módulo de serviço para o banco de dados local de eficiência."""

import pandas as pd

# pylint: disable=import-error
from src.model.efficiency_model import EfficiencyModel


class EfficiencyService:
    """Classe para manipulação dos dados do banco de dados local de eficiência."""

    def __init__(self) -> None:
        self.__efficiency_model = EfficiencyModel()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de eficiência."""
        return self.__efficiency_model.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de eficiência."""
        self.__efficiency_model.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de eficiência."""
        self.__efficiency_model.replace_data(data)
