"""Módulo de Controle para Indicadores Históricos do banco de dados local"""

import pandas as pd

# pylint: disable=import-error
from src.service.historic_ind_service import HistoricIndService


class HistoricIndController:
    """Classe para controle dos dados do banco de dados local de Indicadores Históricos."""

    def __init__(self) -> None:
        self.__historic_ind_service = HistoricIndService()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de Indicadores Históricos."""
        return self.__historic_ind_service.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de Indicadores Históricos."""
        self.__historic_ind_service.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de Indicadores Históricos."""
        self.__historic_ind_service.replace_data(data)
