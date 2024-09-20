"""Módulo de Modelo da tabela PROTHEUS_SD3_PCP."""

import pandas as pd

# pylint: disable=import-error
from src.model.db_totvsdb_model import DBTotvsdbModel

class ProtheusSD3PCPModel():
    """Módulo de modelos da tabela PROTHEUS_SD3_PCP."""

    def __init__(self):
        self.__totvsdb = DBTotvsdbModel()

    def get_data(self, start_date: str, end_date: str) -> pd.DataFrame | None:
        """ Obtém os dados da tabela PROTHEUS_SD3_PCP do banco de dados."""

        # Select
        select_ = """
            SELECT
                SD3.D3_FILIAL as filial,
                SD3.D3_EMISSAO as data_emissao,
                SD3.D3_COD as cod,
                SB1.B1_DESC as descricao,
                SD3.D3_CF as tipo,
                SD3.D3_CUSTO1 as custo,
                SD3.D3_UM as unidade,
                SD3.D3_QUANT as quantidade,
                SD3.D3_GRUPO as grupo,
                SD3.D3_USUARIO as usuario
        """

        # From
        from_ = "FROM SD3000 as SD3 WITH (NOLOCK)"

        # Join
        join_ = """
            INNER JOIN SB1000 SB1 WITH (NOLOCK) ON SD3.D3_COD = SB1.B1_COD
            AND (LEFT(SD3.D3_FILIAL, 2) = SB1.B1_FILIAL) AND SB1.D_E_L_E_T_ <> '*'
        """

        # Where
        where_ = (
            f"WHERE SD3.D_E_L_E_T_ <> '*' AND SD3.D3_EMISSAO BETWEEN '{start_date}' AND '{end_date}'"
            "AND SD3.D3_DOC = 'INVENT' AND SD3.D3_GRUPO != 6"
        )

        query = f"{select_} {from_} {join_} {where_}"

        data = self.__totvsdb.get_data(query)

        return data
