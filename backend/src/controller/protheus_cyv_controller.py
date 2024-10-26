"""Módulo de controle para o DB Protheus CYV."""

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.protheus_cyv_service import ProtheusCYVService


class ProtheusCYVController:
    """Módulo de controle para o DB Protheus CYV."""

    def __init__(self) -> None:
        self.__protheus_cyv_service = ProtheusCYVService()

    def get_massa_data(self) -> pd.DataFrame:
        """Retorna os dados de CYV Massa do DB local.

        Retorna os dados de CYV Massa do DB local, ou um erro 404 caso os dados
        nao estejam disponíveis.

        Returns:
            pd.DataFrame: Dados de CYV Massa do DB local.
        """
        data = self.__protheus_cyv_service.get_massa_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def get_pasta_data(self) -> pd.DataFrame:
        """Retorna os dados de CYV Pasta do DB local.

        Retorna os dados de CYV Pasta do DB local, ou um erro 404 caso os dados
        nao estejam disponíveis.

        Returns:
            pd.DataFrame: Dados de CYV Pasta do DB local.
        """
        data = self.__protheus_cyv_service.get_pasta_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def get_massa_week_data(self) -> pd.DataFrame:
        """Retorna os dados de CYV Massa do DB local por semana.

        Retorna os dados de CYV Massa do DB local por semana, ou um erro 404 caso os dados
        nao estejam disponíveis.

        Returns:
            pd.DataFrame: Dados de CYV Massa do DB local por semana.
        """
        data = self.__protheus_cyv_service.get_massa_week_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def get_pasta_week_data(self) -> pd.DataFrame:
        """Retorna os dados de CYV Pasta do DB local por semana.

        Retorna os dados de CYV Pasta do DB local por semana, ou um erro 404 caso os dados
        nao estejam disponíveis.

        Returns:
            pd.DataFrame: Dados de CYV Pasta do DB local por semana.
        """
        data = self.__protheus_cyv_service.get_pasta_week_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
