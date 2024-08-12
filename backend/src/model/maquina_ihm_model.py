""" Módulo que manipula os dados da tabela maquina_ihm do banco de dados automacao. """

import pandas as pd

# pylint: disable=import-error
from model.db_automacao_model import DBAutomacaoModel


class MaquinaIHMModel:
    """Classe para manipulação dos dados da tabela maquina_ihm."""

    def __init__(self) -> None:
        self.__automacao = DBAutomacaoModel()

    def get_data(self, period: tuple) -> pd.DataFrame:
        """
        Obtém os dados da máquina IHM no intervalo de datas especificado.
        """
        first_day, last_day = period
        first_day = pd.to_datetime(first_day).strftime("%Y-%m-%d")
        last_day = pd.to_datetime(last_day).strftime("%Y-%m-%d")

        # Select
        select_ = "SELECT *"

        # From
        from_ = "FROM AUTOMACAO.dbo.maquina_ihm"

        # Where
        where_ = (
            (f"WHERE data_registro between '{first_day}' and '{last_day}'")
            if first_day != last_day
            else (f"WHERE data_registro >= '{first_day}'")
        )

        # Query
        query = f"{select_} {from_} {where_}"

        return self.__automacao.get_data(query)
