""" Módulo controlador para as informações da máquina qualidade."""

# pylint: disable=import-error
from service.maquina_qualidade_service import MaquinaQualidadeService


class MaquinaQualidadeController:
    """Classe controladora para as informações da máquina qualidade."""

    def __init__(self) -> None:
        self.__maquina_qualidade_service = MaquinaQualidadeService()

    def get_data(self, period: tuple):
        """Obtém os dados da tabela qualidade_ihm."""
        return self.__maquina_qualidade_service.get_data(period)
