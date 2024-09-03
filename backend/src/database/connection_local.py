""" Módulo para conexão com banco de dados SQLite3 """

from sqlalchemy import create_engine
from src.helpers.paths import DB_LOCAL


class ConnectionLocal:
    """Obtém a conexão com o banco de dados local.
    Retorna:
        object: A conexão com o banco de dados.
    """

    def __init__(self):
        self._engine = create_engine(f"sqlite:///{DB_LOCAL}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._engine.dispose()

    def get_session(self):
        """Retorna a sessão atual do banco de dados local.

        Retorna:
            sqlalchemy.orm.session.Session: A sessão do banco de dados local.
        """
        return self._engine
