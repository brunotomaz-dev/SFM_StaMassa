""" Módulo que consulta produtos do banco de dados SB2000 do Protheus. """

import pandas as pd

# pylint: disable=import-error
from src.model.db_totvsdb_model import DBTotvsdbModel


class ProtheusSB2EstoqueModel:
    """
    Classe que realiza a consulta no banco de dados
    e retorna os dados da tabela PROTHEUS_SB2_ESTOQUE.
    """

    def __init__(self) -> None:
        self.__totvsdb = DBTotvsdbModel()

    def get_data(self) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_SB2_ESTOQUE.
        """
        # Select
        select_ = "SELECT SB1.B1_DESC AS produto, SB2.B2_QATU AS quantidade"

        # From
        from_ = "FROM SB2000 SB2 WITH (NOLOCK)"

        # Join
        join_ = """
            INNER JOIN SB1000 SB1 WITH (NOLOCK)
            ON SB1.B1_FILIAL = '01' AND SB1.B1_COD = SB2.B2_COD AND SB1.D_E_L_E_T_<>'*'
            """

        # where
        where_ = """
            WHERE SB2.B2_FILIAL='0101' AND SB2.B2_LOCAL='CF' AND SB1.B1_TIPO='PA'
            AND SB1.B1_LOCPAD='CF' AND SB2.D_E_L_E_T_<>'*'
        """

        # Order By
        order_by_ = "ORDER BY SB2.B2_COD"

        # query
        query = f"{select_} {from_} {join_} {where_} {order_by_}"
        data = self.__totvsdb.get_data(query)
        return data
