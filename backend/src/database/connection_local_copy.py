""" Módulo para conexão com banco de dados SQLite3 """

import sqlite3

# pylint: disable=import-error
from src.helpers.paths import DB_LOCAL


class ConnectionLocal:
    """Obtém a conexão com o banco de dados local.
    Retorna:
        object: A conexão com o banco de dados.
    """

    def __init__(self):
        self._db = DB_LOCAL
        self._connection = None

    def __enter__(self):
        self._connection = sqlite3.connect(self._db)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def get_connection(self):
        """
        Obter conexão

        Returns:
            object: conexão
        """
        return self._connection
