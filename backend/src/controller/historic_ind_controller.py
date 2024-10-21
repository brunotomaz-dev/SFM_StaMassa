"""Módulo de Controle para Indicadores Históricos do banco de dados local"""

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.historic_ind_service import HistoricIndService


class HistoricIndController:
    """Classe para controle dos dados do banco de dados local de Indicadores Históricos."""

    def __init__(self) -> None:
        self.__historic_ind_service = HistoricIndService()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de Indicadores Históricos."""
        data = self.__historic_ind_service.get_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de Indicadores Históricos."""
        self.__historic_ind_service.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de Indicadores Históricos."""
        self.__historic_ind_service.replace_data(data)
