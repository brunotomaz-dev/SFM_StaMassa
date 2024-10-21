""" Módulo controlador para as informações da máquina qualidade."""

from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.maquina_qualidade_service import MaquinaQualidadeService


class MaquinaQualidadeController:
    """Classe controladora para as informações da máquina qualidade."""

    def __init__(self) -> None:
        self.__maquina_qualidade_service = MaquinaQualidadeService()

    def get_data(self, period: tuple):
        """Obtém os dados da tabela qualidade_ihm."""
        data = self.__maquina_qualidade_service.get_data(period)
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
