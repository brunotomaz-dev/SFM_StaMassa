""" Modulo que contem a classe de modelo do banco de dados local """

import pandas as pd

# pylint: disable=E0401
from database.connection_local import ConnectionLocal


class DBAutomacaoLocalModel(ConnectionLocal):
    """Classe para manipulação de dados do banco de dados de automação local."""

    # pylint: disable=W0246
    def __init__(self):
        super().__init__()

    def get_data(self, table: str) -> pd.DataFrame:
        """Obtém os dados do banco de dados local.

        Args:
            query (str): Query SQL.

        Returns:
            pd.DataFrame: DataFrame com os dados.

        Usage:
            >>> from DB_automacao_local_model import DBAutomacaoLocalModel
            >>> db_automacao_local = DBAutomacaoLocalModel()
            >>> query = 'SELECT * FROM tabela'
            >>> df = db_automacao_local.get_data(query)
        """
        try:
            with self as conn:
                query = f"SELECT * FROM {table}"
                connection = conn.get_connection()
                return pd.read_sql_query(query, connection)
        # pylint: disable=W0718
        except Exception as error:
            print(f"Erro ao obter os dados: {error}")
            return None

    def insert_data(self, data: pd.DataFrame, table: str) -> None:
        """Insere dados no banco de dados local."""
        try:
            with self as conn:
                connection = conn.get_connection()
                data.to_sql(table, connection, if_exists="append", index=False)
        # pylint: disable=W0718
        except Exception as error:
            print(f"Erro ao inserir os dados: {error}")

    def replace_data(self, data: pd.DataFrame, table: str) -> None:
        """Atualiza dados no banco de dados local."""
        try:
            with self as conn:
                connection = conn.get_connection()
                data.to_sql(table, connection, if_exists="replace", index=False)
        # pylint: disable=W0718
        except Exception as error:
            print(f"Erro ao atualizar os dados: {error}")
