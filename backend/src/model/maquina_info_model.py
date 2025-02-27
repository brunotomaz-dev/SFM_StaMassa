""" Módulo responsável por realizar a consulta no banco de dados
e retornar os dados da tabela maquina_info. """

import pandas as pd

# pylint: disable=import-error
from src.model.db_automacao_model import DBAutomacaoModel


class MaquinaInfoModel:
    """
    Classe responsável por realizar a consulta no banco de dados
    e retornar os dados da tabela maquina_info.
    """

    def __init__(self) -> None:
        self.__automacao = DBAutomacaoModel()

    def get_data(self, period: tuple) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela maquina_info.
        """
        first_day, last_day = period
        first_day = pd.to_datetime(first_day).strftime("%Y-%m-%d")
        last_day = pd.to_datetime(last_day).strftime("%Y-%m-%d")

        # Select
        select_ = (
            "SELECT"
            " t1.maquina_id,"
            " (SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro"
            " ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as linha,"
            " (SELECT TOP 1 t2.fabrica FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro"
            " ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as fabrica,"
            " t1.status,"
            " t1.turno,"
            " t1.ciclo_1_min,"
            " t1.contagem_total_ciclos,"
            " t1.contagem_total_produzido,"
            " t1.data_registro,"
            " t1.hora_registro"
        )

        # From
        from_ = "FROM AUTOMACAO.dbo.maquina_info t1"

        # Where
        where_ = (
            (f"WHERE data_registro between '{first_day}' and '{last_day}'")
            if first_day != last_day
            else (f"WHERE data_registro >= '{first_day}'")
        )

        # Order by
        order_by = " ORDER BY t1.data_registro DESC, t1.hora_registro DESC"

        # Query
        query = f"{select_} {from_} {where_} {order_by}"
        data = self.__automacao.get_data(query)

        return data

    def get_data_cycle(self, period: tuple) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela maquina_info.
        """
        first_day, last_day = period
        first_day = pd.to_datetime(first_day).strftime("%Y-%m-%d")
        last_day = pd.to_datetime(last_day).strftime("%Y-%m-%d")

        # Select
        select_ = """
            SELECT
                [data_registro]
                ,[maquina_id]
                ,[turno]
                ,[produto]
                ,AVG([ciclo_1_min]) AS media_ciclo
        """

        # From
        from_ = "FROM AUTOMACAO.dbo.maquina_info"

        # Where
        where_ = (
            (f"WHERE data_registro between '{first_day}' and '{last_day}' AND status = 'true'")
            if first_day != last_day
            else (f"WHERE data_registro >= '{first_day}' and status = 'true'")
        )

        # Group by
        group_by = "GROUP BY data_registro, maquina_id, turno, produto"

        # Order by
        order_by = " ORDER BY data_registro DESC, maquina_id DESC"

        # Query
        query = f"{select_} {from_} {where_} {group_by} {order_by}"
        data = self.__automacao.get_data(query)

        return data

    def get_production_data(self, period: tuple) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela maquina_info.
        """
        first_day, last_day = period
        first_day = pd.to_datetime(first_day).strftime("%Y-%m-%d")
        last_day = pd.to_datetime(last_day).strftime("%Y-%m-%d")

        # Where
        where_date = (
            f"BETWEEN '{first_day}' and '{last_day}' "
            if first_day != last_day
            else f">= '{first_day}'"
        )

        query = f"""
            SELECT * FROM (
                SELECT
                    (
                        SELECT TOP 1 t2.fabrica
                        FROM AUTOMACAO.dbo.maquina_cadastro t2
                        WHERE t2.maquina_id = t1.maquina_id
                        AND t2.data_registro <= t1.data_registro
                        ORDER BY t2.data_registro DESC, t2.hora_registro DESC
                    ) as fabrica,
                    (
                        SELECT TOP 1 t2.linha
                        FROM AUTOMACAO.dbo.maquina_cadastro t2
                        WHERE t2.maquina_id = t1.maquina_id
                        AND t2.data_registro <= t1.data_registro
                        ORDER BY t2.data_registro DESC, t2.hora_registro DESC
                    ) as linha,
                    t1.maquina_id,
                    t1.turno,
                    t1.status,
                    t1.produto,
                    t1.contagem_total_ciclos as total_ciclos,
                    t1.contagem_total_produzido as total_produzido,
                    t1.data_registro,
                    t1.hora_registro,
                    (
                        SELECT TOP 1 t2.produto_id
                        FROM AUTOMACAO.dbo.maquina_produto t2
                        WHERE t2.maquina_id = t1.maquina_id
                        AND t2.data_registro <= t1.data_registro
                        ORDER BY t2.data_registro DESC, t2.hora_registro DESC
                    ) as produto_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY t1.data_registro, t1.turno, t1.maquina_id
                        ORDER BY t1.data_registro DESC, t1.hora_registro DESC
                    ) AS rn
                FROM AUTOMACAO.dbo.maquina_info t1
            ) AS t
            WHERE rn = 1
            AND data_registro {where_date}
            AND hora_registro > '00:01'
            ORDER BY data_registro DESC, linha
        """

        return self.__automacao.get_data(query)

    def get_production_data_by_period(self, period: str) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela maquina_info.
        """

        first_day = pd.to_datetime(period).strftime("%Y-%m-%d")

        # Select
        select_ = """
            SELECT
                linha,
                maquina_id,
                turno,
                contagem_total_ciclos as total_ciclos,
                contagem_total_produzido as total_produzido_sensor,
                B1_DESC as produto,
                data_registro
        """

        # From
        from_ = """
            FROM (
                SELECT
                    (SELECT TOP 1 t2.fabrica FROM AUTOMACAO.dbo.maquina_cadastro t2
                    WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro
                    ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as fabrica,
                    (SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2
                    WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro
                    ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as linha,
                    t1.maquina_id,
                    t1.turno,
                    t1.contagem_total_ciclos,
                    t1.contagem_total_produzido,
                    (SELECT TOP 1 t2.produto_id FROM AUTOMACAO.dbo.maquina_produto t2
                    WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro
                    ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as produto_id,
                    t1.data_registro,
                    t1.hora_registro,
                    ROW_NUMBER() OVER (
                        PARTITION BY t1.data_registro, t1.turno, t1.maquina_id
                        ORDER BY t1.data_registro DESC, t1.hora_registro DESC) AS rn
                FROM AUTOMACAO.dbo.maquina_info t1
            ) AS t
        """

        # Join
        join_ = """
            INNER JOIN
                TOTVSDB.dbo.SB1000 SB1 WITH (NOLOCK)
                ON SB1.B1_FILIAL = '01' AND SB1.B1_COD = t.produto_id AND SB1.D_E_L_E_T_<>'*'
        """

        # Where
        where_ = f"""
            WHERE t.rn = 1
                AND hora_registro > '00:01'
                AND data_registro = '{first_day}'"""

        # Order by
        order_by = "ORDER BY data_registro DESC, linha"

        # Query
        query = f"{select_} {from_} {join_} {where_} {order_by}"

        return self.__automacao.get_data(query)
