"""Módulo de serviço para tabela local Info/IHM."""

import pandas as pd

# pylint: disable=import-error
from src.model.info_ihm_model import InfoIHMModel


class InfoIHMService:
    """Classe para manipulação dos dados da tabela local Info/IHM."""

    def __init__(self) -> None:
        self.__info_ihm_model = InfoIHMModel()

    def get_data(self) -> pd.DataFrame:
        """Obtém os dados da tabela local Info/IHM."""
        return self.__info_ihm_model.get_data()

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados na tabela local Info/IHM."""
        self.__info_ihm_model.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados na tabela local Info/IHM."""
        self.__info_ihm_model.replace_data(data)
