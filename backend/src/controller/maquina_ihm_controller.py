""" Módulo que faz o controle dos dados de máquina IHM. """

from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.maquina_ihm_service import MaquinaIHMService


class MaquinaIHMController:
    """Classe de controle para dados de máquina IHM."""

    def __init__(self) -> None:
        self.__maquina_ihm_service = MaquinaIHMService()

    def get_data(self, period: tuple):
        """Obtém dados da tabela maquina_ihm."""
        data = self.__maquina_ihm_service.get_data(period)

        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
