"""Módulo de modelo para o DB Protheus CYV."""
from calendar import month

import pandas as pd

# pylint: disable=import-error
from src.model.db_totvsdb_model import DBTotvsdbModel

class ProtheusCYVModel:
    """Classe que realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_CYV."""

    def __init__(self) -> None:
        self.__totvsdb = DBTotvsdbModel()

    def get_massa_data(self) -> pd.DataFrame:
        """Realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_CYV."""

        # Recupera a data de hoje
        today = pd.Timestamp.today()

        # Primeiro dia do ano atual caso estejamos até em junho
        if today.month >= 6:
            first_day = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        # Primeiro dia do semestre caso já tenhamos passado junho
        else:
            first_day = today - pd.DateOffset(months=6)
            first_day = first_day.replace(day=1).strftime("%Y-%m-%d")

        select_ = (
            'SELECT T1.CYV_CDMQ AS "Codigo_Maquina"'
            ', T2.CYB_DSMQ AS "Descricao_Maquina"'
            ', T1.CYV_QTATRP AS "Quantidade_Atropelamento"'
            ', T6.OX_DESCR AS "Produto"'
            ', T1.CYV_DTRPBG AS "Data_Registro"'
            ', T1.CYV_HRRPBG AS "Hora_Registro"'
            ', T1.CYV_CDUSRP AS "Usuario_Registro"'
            ", COALESCE("
            "CASE WHEN CHARINDEX(T1.CYV_CDUSRP, T3.X6_CONTEUD) > 0 THEN 'Fab. 1' END,"
            "CASE WHEN CHARINDEX(T1.CYV_CDUSRP, T4.X6_CONTEUD) > 0 THEN 'Fab. 2' END,"
            "'Não identificado'"
            ') AS "Fabrica"'
        )

        from_ = "FROM CYV000 (NOLOCK) AS T1"

        join_ = (
            "JOIN CYB000 (NOLOCK) AS T2 ON T1.CYV_FILIAL = T2.CYB_FILIAL "
            "AND T1.CYV_CDMQ = T2.CYB_CDMQ AND T2.D_E_L_E_T_ <> '*'"
            "LEFT JOIN SX6000 (NOLOCK) AS T3 ON T3.X6_VAR = 'MV_X_USRF1' "
            "LEFT JOIN SX6000 (NOLOCK) AS T4 ON T4.X6_VAR = 'MV_X_USRF2' "
            "JOIN V9_000 (NOLOCK) AS T5 ON T1.CYV_CDMQ = T5.V9__MAQ AND T1.CYV_NRORPO = T5.V9__OP "
            "AND T1.CYV_DTRPBG = T5.V9__DTINI AND T1.CYV_HRRPBG = T5.V9__HRINI "
            "AND T5.V9__STATUS = 1 AND T5.D_E_L_E_T_ <> '*' "
            "JOIN SOX000 (NOLOCK) AS T6 ON T5.V9__FORM = T6.OX_FORM AND T6.D_E_L_E_T_ <> '*'"
        )

        where_ = (
            "WHERE T1.D_E_L_E_T_ <> '*' AND T1.CYV_FILIAL = '0101' AND T1.CYV_CDMQ LIKE 'AMS%' "
            f"AND T1.CYV_DTRPBG >= '{first_day}'"
        )

        order_by_ = "ORDER BY T1.CYV_DTRPBG, T1.CYV_CDMQ, T1.CYV_HRRPBG"

        # Cria a query
        query = f"{select_} {from_} {join_} {where_} {order_by_}"

        # Executa a query
        data = self.__totvsdb.get_data(query)

        return data

    def get_pasta_data(self) -> pd.DataFrame:
        """Realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_CYV."""

        # Recupera a data de hoje
        today = pd.Timestamp.today()

        # Primeiro dia do ano atual caso estejamos até em junho
        if today.month >= 6:
            first_day = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        # Primeiro dia do semestre caso já tenhamos passado junho
        else:
            first_day = today - pd.DateOffset(months=6)
            first_day = first_day.replace(day=1).strftime("%Y-%m-%d")

        select_ = (
            'SELECT T1.CYV_CDMQ AS "Codigo_Maquina"'
            ', T2.CYB_DSMQ AS "Descricao_Maquina"'
            ', T1.CYV_QTATRP AS "Quantidade_Atropelamento"'
            ', T6.OX_DESCR AS "Produto"'
            ', T1.CYV_DTRPBG AS "Data_Registro"'
            ', T1.CYV_HRRPBG AS "Hora_Registro"'
            ', T1.CYV_CDUSRP AS "Usuario_Registro"'
            ", COALESCE("
            "CASE WHEN CHARINDEX('1', T2.CYB_X_FABR) > 0 THEN 'Fab. 1' END,"
            "CASE WHEN CHARINDEX('2', T2.CYB_X_FABR) > 0 THEN 'Fab. 2' END,"
            "'Não identificado'"
            ') AS "Fabrica"'
        )

        from_ = "FROM CYV000 (NOLOCK) AS T1"

        join_ = (
            "JOIN CYB000 (NOLOCK) AS T2 ON T1.CYV_FILIAL = T2.CYB_FILIAL "
            "AND T1.CYV_CDMQ = T2.CYB_CDMQ AND T2.D_E_L_E_T_ <> '*'"
            "JOIN V9_000 (NOLOCK) AS T5 ON T1.CYV_CDMQ = T5.V9__MAQ AND T1.CYV_NRORPO = T5.V9__OP "
            "AND T1.CYV_DTRPBG = T5.V9__DTINI AND T1.CYV_HRRPBG = T5.V9__HRINI "
            "AND T5.V9__STATUS = 1 AND T5.D_E_L_E_T_ <> '*' "
            "JOIN SOX000 (NOLOCK) AS T6 ON T5.V9__FORM = T6.OX_FORM AND T6.D_E_L_E_T_ <> '*'"
        )

        where_ = (
            "WHERE T1.D_E_L_E_T_ <> '*' AND T1.CYV_FILIAL = '0101' AND T1.CYV_CDMQ LIKE 'RET%' "
            f"AND T1.CYV_DTRPBG >= '{first_day}'"
        )

        order_by_ = "ORDER BY T1.CYV_DTRPBG, T1.CYV_CDMQ, T1.CYV_HRRPBG"

        # Cria a query
        query = f"{select_} {from_} {join_} {where_} {order_by_}"

        # Executa a query
        data = self.__totvsdb.get_data(query)

        return data