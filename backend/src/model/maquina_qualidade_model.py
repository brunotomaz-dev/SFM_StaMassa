"""Módulo que modela a tabela qualidade_ihm no banco de dados."""

import pandas as pd

# pylint: disable=import-error
from src.model.db_automacao_model import DBAutomacaoModel


class MaquinaQualidadeModel:
    """Classe que modela a tabela qualidade_ihm no banco de dados."""

    def __init__(self) -> None:
        self.__db_automacao = DBAutomacaoModel()

    def get_data(self, period: tuple) -> pd.DataFrame:
        """Consulta o banco de dados e retorna os dados da tabela qualidade_ihm."""

        first_day, last_day = period
        first_day = pd.to_datetime(first_day).strftime("%Y-%m-%d")
        last_day = pd.to_datetime(last_day).strftime("%Y-%m-%d")

        # Select
        select_ = "SELECT *"

        # From
        from_ = "FROM AUTOMACAO.dbo.qualidade_ihm"

        # Where
        where_ = (
            (f"WHERE data_registro between '{first_day}' and '{last_day}'")
            if first_day != last_day
            else (f"WHERE data_registro >= '{first_day}'")
        )

        # Query
        query = f"{select_} {from_} {where_}"

        # Executa a query
        df = self.__db_automacao.get_data(query)

        return df
