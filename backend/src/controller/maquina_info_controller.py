"""Módulo controlador para as informações da máquina."""

# pylint: disable=import-error
from service.maquina_info_service import MaquinaInfoService


class MaquinaInfoController:
    """Classe controladora para as informações da máquina."""

    def __init__(self) -> None:
        self.__maquina_info_service = MaquinaInfoService()

    def get_data(self, period: tuple):
        """Obtém os dados da tabela maquina_info."""
        return self.__maquina_info_service.get_data(period)

    def get_production_data(self, period: tuple):
        """Obtém os dados de produção da máquina."""
        return self.__maquina_info_service.get_production_data(period)
