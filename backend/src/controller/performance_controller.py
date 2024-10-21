""" Módulo de controle para performance do banco de dados local """

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.performance_service import PerformanceService


class PerformanceController:
    """Classe para controle dos dados do banco de dados local de performance."""

    def __init__(self) -> None:
        self.__performance_service = PerformanceService()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de performance."""
        data = self.__performance_service.get_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de performance."""
        self.__performance_service.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de performance."""
        self.__performance_service.replace_data(data)
