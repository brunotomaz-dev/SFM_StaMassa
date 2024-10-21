"""Módulo controlador para as informações da máquina."""

from fastapi import status
from fastapi.responses import JSONResponse

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

    def get_production_data(self, period: tuple):
        """Obtém os dados de produção da máquina."""
        data = self.__maquina_info_service.get_production_data(period)
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
