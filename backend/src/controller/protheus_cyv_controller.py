"""Módulo de controle para o DB Protheus CYV."""

import pandas as pd

# pylint: disable=import-error
from src.service.protheus_cyv_service import ProtheusCYVService


class ProtheusCYVController:

    def __init__(self) -> None:
        self.__protheus_cyv_service = ProtheusCYVService()

    def get_massa_data(self) -> pd.DataFrame:
        return self.__protheus_cyv_service.get_massa_data()

    def get_pasta_data(self) -> pd.DataFrame:
        return self.__protheus_cyv_service.get_pasta_data()

    def get_massa_week_data(self) -> pd.DataFrame:
        return self.__protheus_cyv_service.get_massa_week_data()

    def get_pasta_week_data(self) -> pd.DataFrame:
        return self.__protheus_cyv_service.get_pasta_week_data()
