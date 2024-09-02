""" Modulo que contem a classe de modelo do banco de dados local """

import pandas as pd
from src.database.connection_local import ConnectionLocal


class DBAutomacaoLocalModel(ConnectionLocal):
    """Classe para manipulação de dados do banco de dados de automação local."""

    # pylint: disable=W0246
    def __init__(self):
        super().__init__()

    def get_data(self, table: str) -> pd.DataFrame | None:
        """Obtém dados do banco de dados local."""
        conn = None
        try:
            conn = self.get_session()
            return pd.read_sql_query(f"SELECT * FROM {table}", conn)

        # pylint: disable=W0718
        except Exception as error:
            print(f"Erro ao obter os dados: {error}")
            return None
        finally:
            if conn:
                conn.dispose()

    def insert_data(self, data: pd.DataFrame, table: str) -> None:
        """Insere dados no banco de dados local."""
        conn = None
        try:
            conn = self.get_session()
            data.to_sql(table, conn, if_exists="append", index=False)

        # pylint: disable=W0718
        except Exception as error:
            print(f"Erro ao inserir os dados: {error}")

        finally:
            if conn:
                conn.dispose()

    def replace_data(self, data: pd.DataFrame, table: str) -> None:
        """Atualiza dados no banco de dados local."""
        conn = None
        try:
            conn = self.get_session()
            data.to_sql(table, conn, if_exists="replace", index=False)

        # pylint: disable=W0718
        except Exception as error:
            print(f"Erro ao atualizar os dados: {error}")

        finally:
            if conn:
                conn.dispose()
