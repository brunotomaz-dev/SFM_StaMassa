""" Módulo que consulta produtos do banco de dados SB1000 do Protheus. """

import pandas as pd

# pylint: disable=import-error
from src.model.db_totvsdb_model import DBTotvsdbModel

class ProtheusSB1ProdutosModel:
    """
    Classe que realiza a consulta no banco de dados
    e retorna os dados da tabela PROTHEUS_SB1_PRODUTOS.
    """

    def __init__(self) -> None:
        self.__totvsdb = DBTotvsdbModel()

    def get_data(self) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_SB1_PRODUTOS.
        """
        # Select
        select_ = "SELECT B1_COD as produto_id, B1_DESC as descricao"

        # From
        from_ = "FROM SB1000 SB1"

        # where
        where_ = "WHERE SB1.B1_FILIAL = '01' AND SB1.D_E_L_E_T_ <> '*'"

        # query
        query = f"{select_} {from_} {where_}"
        data = self.__totvsdb.get_data(query)
        return data
