"""Módulo de controle para tabela info_ihm do banco de dados local"""

import pandas as pd

# pylint: disable=import-error
from src.service.info_ihm import InfoIHMService


class InfoIHMController:
    """Classe para controle dos dados da tabela info_ihm do banco de dados local."""

    def __init__(self) -> None:
        self.__info_ihm_service = InfoIHMService()

    def get_data(self) -> pd.DataFrame:
        """Obtém os dados da tabela info_ihm do banco de dados local."""
        return self.__info_ihm_service.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados na tabela info_ihm do banco de dados local."""
        self.__info_ihm_service.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados na tabela info_ihm do banco de dados local."""
        self.__info_ihm_service.replace_data(data)
