"""Módulo controlador para as informações da máquina."""

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse
from src.functions.date_f import get_date, get_first_and_last_day_of_month

# pylint: disable=import-error
from src.service.maquina_info_service import MaquinaInfoService


class MaquinaInfoController:
    """Classe controladora para as informações da máquina."""

    def __init__(self) -> None:
        self.__maquina_info_service = MaquinaInfoService()

    def get_data(self, period: tuple):
        """Obtém os dados da tabela maquina_info."""
        data = self.__maquina_info_service.get_data(period)
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def get_data_cycle(self, period: tuple):
        """Obtém os dados da tabela maquina_info."""

        start, end = period

        if start is not None and end is not None:
            data = self.__maquina_info_service.get_data_cycle(period)
        else:
            _, end = get_first_and_last_day_of_month()
            today = get_date()
            start = today - pd.DateOffset(days=31)

            start = start.strftime("%Y-%m-%d")
            end = end.strftime("%Y-%m-%d")

            data = self.__maquina_info_service.get_data_cycle((start, end))

        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def get_pure_data(self, period: tuple):
        """Obtém os dados da tabela maquina_info."""
        data = self.__maquina_info_service.get_pure_data(period)
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def get_production_data(self, period: tuple):
        """Obtém os dados de produção da máquina."""
        data = self.__maquina_info_service.get_production_data(period)
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def get_production_data_by_day(self, day: str):
        """Obtém os dados de produção da máquina por dia."""
        data = self.__maquina_info_service.get_production_data_by_period(day)
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
