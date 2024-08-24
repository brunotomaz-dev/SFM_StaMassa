"""Módulo de serviço para o banco de dados local de performance."""

import pandas as pd

# pylint: disable=import-error
from src.model.performance_model import PerformanceModel


class PerformanceService:
    """Classe para manipulação dos dados do banco de dados local de performance."""

    def __init__(self) -> None:
        self.__performance_model = PerformanceModel()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de performance."""
        return self.__performance_model.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de performance."""
        self.__performance_model.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de performance."""
        self.__performance_model.replace_data(data)
