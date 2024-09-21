"""Módulo para manipulação de dados do banco de dados Totvs."""

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DatabaseError

# pylint: disable=E0401
from src.database.connection import Connection


class DBTotvsdbModel(Connection):
    """Classe para manipulação de dados do banco de dados Totvs."""

    # pylint: disable=W0246
    def __init__(self):
        super().__init__()

    def get_data(self, query: str) -> pd.DataFrame:
        """
        Recupera os dados do banco de dados do Protheus.

        Args:
            query (str): Query SQL.

        Returns:
            pd.DataFrame: DataFrame com os dados.

        """

        conn: Engine | None = None
        try:
            conn = self.get_connection_totvsdb()
            return pd.read_sql(query, conn)
        except DatabaseError as error:
            print(f"Erro ao obter os dados: {error}")
        finally:
            if conn:
                conn.dispose()
