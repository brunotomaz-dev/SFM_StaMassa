"""Módulo de serviço para o banco de dados local de produção."""

import pandas as pd

# pylint: disable=import-error
from src.model.production_model import ProductionModel


class ProductionService:
    """Classe para manipulação dos dados do banco de dados local de produção."""

    def __init__(self) -> None:
        self.__production_model = ProductionModel()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de produção."""
        return self.__production_model.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de produção."""
        self.__production_model.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de produção."""
        self.__production_model.replace_data(data)
