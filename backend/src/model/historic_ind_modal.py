"""Módulo para modelo de Indicadores Históricos do banco de dados local"""

import pandas as pd

# pylint: disable=import-error
from src.helpers.variables import LocalTables
from src.model.db_automacao_local_model import DBAutomacaoLocalModel


class HistoricInd:
    """Classe que modela a tabela de indicadores históricos do banco de dados local"""

    def __init__(self) -> None:
        self.__db_automacao_local = DBAutomacaoLocalModel()
        self.__table = LocalTables.HISTORIC_IND.value

    def get_data(self) -> pd.DataFrame:
        """Consulta o banco de dados e retorna os dados da tabela de indicadores históricos"""

        return self.__db_automacao_local.get_data(self.__table)

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere os dados na tabela de indicadores históricos do banco de dados local"""

        self.__db_automacao_local.insert_data(data, self.__table)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui os dados na tabela de indicadores históricos do banco de dados local"""

        self.__db_automacao_local.replace_data(data, self.__table)
