""" Módulo que faz o controle dos dados de máquina IHM. """

# pylint: disable=import-error
from service.maquina_ihm_service import MaquinaIHMService


class MaquinaIHMController:
    """Classe de controle para dados de máquina IHM."""

    def __init__(self) -> None:
        self.__maquina_ihm_service = MaquinaIHMService()

    def get_data(self, period: tuple):
        """Obtém dados da tabela maquina_ihm."""
        return self.__maquina_ihm_service.get_data(period)
