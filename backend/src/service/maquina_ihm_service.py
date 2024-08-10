""" Módulo responsável por tratar os dados da máquina info e IHM. """

import numpy as np

# pylint: disable=import-error
from src.model.maquina_ihm_model import MaquinaIHMModel
from src.service.functions.clean_data import CleanData


class MaquinaIHMService:
    """Classe responsável por tratar os dados da máquina info e IHM."""

    def __init__(self) -> None:
        self.__maquina_ihm = MaquinaIHMModel()
        self.__clean_data = CleanData()

    def get_data(self, period: tuple):
        """Método responsável por tratar os dados da máquina info e IHM."""
        # Consulta os dados da máquina
        data = self.__maquina_ihm.get_data(period)

        # Verifica se a consulta retornou dados
        if data is not None:

            # Limpa os dados de forma básica
            data = self.__clean_data.clean_data(data)

            # Se a coluna equipamento estiver entre os valoras 1 a 14(str) cria nova coluna
            data["s_backup"] = np.where(
                data.equipamento.astype(str).str.isdigit(), data.equipamento, None
            )

            # Remove os valores numéricos da coluna equipamento
            data.equipamento = np.where(
                data.equipamento.astype(str).str.isdigit(), None, data.equipamento
            )

        return data
