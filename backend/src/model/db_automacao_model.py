""" Este módulo faz a comunicação principal com o banco de dados """

import pandas as pd
from sqlalchemy.exc import DatabaseError

# pylint: disable=E0401
from src.database.connection import Connection


class DBAutomacaoModel(Connection):
    """Classe para manipulação de dados do banco de dados de automação."""

    # pylint: disable=W0246
    def __init__(self):
        super().__init__()

    def get_data(self, query: str) -> pd.DataFrame:
        """Obtém os dados do banco de dados.

        Args:
            query (str): Query SQL.

        Returns:
            pd.DataFrame: DataFrame com os dados.

        Usage:
            >>> from DB_automacao_model import DBAutomacaoModel
            >>> db_automacao = DBAutomacaoModel()
            >>> query = 'SELECT * FROM tabela'
            >>> df = db_automacao.get_data(query)
        """
        try:
            conn = self.get_connection_automacao()
            return pd.read_sql(query, conn)
        except DatabaseError as error:
            print(f"Erro ao obter os dados: {error}")
            return None
        finally:
            if conn:
                conn.dispose()

    def insert_data(self, query: str) -> None:
        """Insere dados no banco de dados."""

    def update_data(self, query: str) -> None:
        """Atualiza dados no banco de dados."""
