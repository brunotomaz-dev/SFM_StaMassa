"""Módulo de serviço para o banco de dados local de reparo."""

import pandas as pd

# pylint: disable=import-error
from src.model.reparo_model import ReparoModel


class ReparoService:
    """Classe para manipulação dos dados do banco de dados local de reparo."""

    def __init__(self) -> None:
        self.__reparo_model = ReparoModel()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de reparo."""
        return self.__reparo_model.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de reparo."""
        self.__reparo_model.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de reparo."""
        self.__reparo_model.replace_data(data)
