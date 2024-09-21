"""Módulo de Modelo da tabela PROTHEUS_SD3_PRODUCTION."""

import pandas as pd

# pylint: disable=import-error
from src.model.db_totvsdb_model import DBTotvsdbModel


class ProtheusSD3ProductionModel:
    """
    Classe que realiza a consulta no banco de dados
    e retorna os dados da tabela PROTHEUS_SD3_PRODUCTION.
    """

    def __init__(self) -> None:
        self.__totvsdb = DBTotvsdbModel()

    def get_data(self) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_SD3_PRODUCTION.
        """
        # Recupera a data de hoje
        today = pd.Timestamp.today()

        # Primeiro dia do ano atual caso estejamos até em junho
        if today.month >= 6:
            first_day = today.replace(month=1, day=1).strftime("%Y%m%d")
        # Primeiro dia do semestre caso já tenhamos passado junho
        else:
            first_day = today - pd.DateOffset(months=6)
            first_day = first_day.replace(day=1).strftime("%Y%m%d")

        # Select
        select_ = """
        SELECT
            T9_NOME AS MAQUINA
            , B1_DESC AS PRODUTO
            , D3_QUANT AS QTD
            , D3_UM AS UNIDADE
            , D3_EMISSAO AS EMISSAO
            , CYV_HRRPBG AS HORA
            , CYV_CCCA05 AS LOTE
            , CYV_CDUSRP AS USUARIO
            , COALESCE(
            CASE WHEN CHARINDEX(CYV.CYV_CDUSRP, SX6_1.X6_CONTEUD) > 0 THEN 'Fab. 1' END,
            CASE WHEN CHARINDEX(CYV.CYV_CDUSRP, SX6_2.X6_CONTEUD) > 0 THEN 'Fab. 2' END,
            'Não Identificado') AS FABRICA
        """

        # From
        from_ = "FROM SD3000 SD3 WITH (NOLOCK)"

        # join
        join_ = """
        LEFT JOIN SB1000 SB1 WITH (NOLOCK)
            ON SB1.B1_FILIAL = '01' AND SB1.B1_COD = SD3.D3_COD AND SB1.D_E_L_E_T_ <> '*'
        LEFT JOIN CYV000 CYV WITH (NOLOCK)
            ON CYV.CYV_FILIAL = SD3.D3_FILIAL AND CYV.CYV_NRRPET = SD3.D3_IDENT
            AND CYV.D_E_L_E_T_ <> '*'
        LEFT JOIN ST9000 ST9 WITH (NOLOCK)
            ON ST9.T9_CODBEM = CYV.CYV_CDMQ AND ST9.D_E_L_E_T_ <> '*'
        LEFT JOIN SX6000 SX6_1 WITH (NOLOCK)
            ON SX6_1.X6_VAR = 'MV_X_USRF1' AND SX6_1.D_E_L_E_T_ <> '*'
        LEFT JOIN SX6000 SX6_2 WITH (NOLOCK)
            ON SX6_2.X6_VAR = 'MV_X_USRF2' AND SX6_2.D_E_L_E_T_ <> '*'
        """

        # Where
        where_ = f"""
        WHERE
            SD3.D3_FILIAL = '0101' AND SD3.D3_LOCAL = 'CF'
            AND SB1.B1_TIPO = 'PA' AND SD3.D3_CF = 'PR0' AND SD3.D3_ESTORNO <> 'S'
            AND SD3.D3_EMISSAO >= '{first_day}' AND SD3.D_E_L_E_T_ <> '*'
        """

        # Order by
        order_by_ = "ORDER BY SD3.D3_EMISSAO DESC, CYV.CYV_HRRPBG DESC"

        # Criando a query
        query = f"{select_} {from_} {join_} {where_} {order_by_}"
        data = self.__totvsdb.get_data(query)
        return data
