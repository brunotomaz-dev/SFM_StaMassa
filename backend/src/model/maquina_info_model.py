""" Módulo responsável por realizar a consulta no banco de dados
e retornar os dados da tabela maquina_info. """

import pandas as pd

# pylint: disable=import-error
from model.db_automacao_model import DBAutomacaoModel


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

    def get_production_data(self, period: tuple) -> pd.DataFrame:
        """
        Realiza a consulta no banco de dados e retorna os dados da tabela maquina_info.
        """
        first_day, last_day = period
        first_day = pd.to_datetime(first_day).strftime("%Y-%m-%d")
        last_day = pd.to_datetime(last_day).strftime("%Y-%m-%d")

        # Select
        select_ = "SELECT *"

        # From
        from_ = (
            "FROM ( "
            "SELECT "
            "(SELECT TOP 1 t2.fabrica FROM AUTOMACAO.dbo.maquina_cadastro t2 "
            "WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro "
            "ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as fabrica, "
            "(SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2 "
            "WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro "
            "ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as linha, "
            "t1.maquina_id, "
            "t1.turno, "
            "t1.status, "
            "t1.contagem_total_ciclos as total_ciclos, "
            "t1.contagem_total_produzido as total_produzido, "
            "t1.data_registro, "
            "t1.hora_registro, "
            "ROW_NUMBER() OVER ( "
            "PARTITION BY t1.data_registro, t1.turno, t1.maquina_id "
            "ORDER BY t1.data_registro DESC, t1.hora_registro DESC"
            ") AS rn "
            "FROM AUTOMACAO.dbo.maquina_info t1 "
            ") AS t "
        )

        # Where
        where_ = (
            (
                f"WHERE rn = 1 AND data_registro between '{first_day}' and '{last_day}' "
                "AND hora_registro > '00:01'"
            )
            if first_day != last_day
            else (f"WHERE rn = 1 AND data_registro >= '{first_day}' AND hora_registro > '00:01'")
        )

        # Order by
        order_by = "ORDER BY data_registro DESC, linha"

        # Query
        query = f"{select_} {from_} {where_} {order_by}"

        return self.__automacao.get_data(query)
