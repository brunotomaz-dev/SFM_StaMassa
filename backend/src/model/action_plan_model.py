""" Módulo de Modelo para tabela action_plan """

import pandas as pd
from src.helpers.variables import LocalTables
from src.model.db_automacao_local_model import DBAutomacaoLocalModel


class ActionPlanModel:
    """Classe que modela a tabela de action_plan do banco de dados local"""

    def __init__(self) -> None:
        self.__db_automacao_local = DBAutomacaoLocalModel()
        self.__table = LocalTables.ACTION_PLAN.value

    def create_table(self) -> None:
        """Cria a tabela de action_plan no banco de dados local"""

        schema = """
            Data TEXT,
            Indicador TEXT,
            Dias_em_aberto INTEGER,
            Prioridade TEXT,
            Descricao_do_problema TEXT,
            Impacto TEXT,
            Causa_raiz TEXT,
            Contencao TEXT,
            Solucao TEXT,
            Feedback TEXT,
            Responsavel TEXT,
            Conclusao BOOLEAN
        """

        self.__db_automacao_local.create_table(self.__table, schema)

    def get_data(self) -> pd.DataFrame:
        """Consulta o banco de dados e retorna os dados da tabela de action_plan"""

        return self.__db_automacao_local.get_data(self.__table)

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere os dados na tabela de action_plan do banco de dados local"""

        self.__db_automacao_local.insert_data(data, self.__table)

    def update_data(self, index: int, changes: dict) -> None:
        """Substitui os dados na tabela de action_plan do banco de dados local"""
        # Busca os dados no banco de dados
        df = self.get_data()

        # Verifica se o índice existe
        if df is None or index not in df.index:
            raise ValueError("Índice não encontrado")

        # Atualiza os dados
        for column, value in changes.items():
            df.at[index, column] = value

        # Substitui os dados
        self.__db_automacao_local.replace_data(df, self.__table)

    def delete_data(self, index: int) -> None:
        """Deleta os dados na tabela de action_plan do banco de dados local"""
        # Busca os dados no banco de dados
        df = self.get_data()

        # Verifica se o índice existe
        if df is None or index not in df.index:
            raise ValueError("Índice não encontrado")

        # Deleta os dados
        df = df.drop(index)

        # Substitui os dados
        self.__db_automacao_local.replace_data(df, self.__table)
