""" Módulo de serviço para action plan do banco de dados local."""

import pandas as pd
from src.model.action_plan_model import ActionPlanModel


class ActionPlanService:
    """Classe de serviço para manipulação dos dados do banco de dados local de action plan.

    Utiliza o modelo de dados ActionPlanModel para realizar operações no banco de dados local.
    """

    def __init__(self) -> None:
        self.__action_plan_model = ActionPlanModel()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de action plan."""
        return self.__action_plan_model.get_data()

    def insert_data(self, data: pd.DataFrame):
        """Insere dados no banco de dados local de action plan."""
        self.__action_plan_model.insert_data(data)

    def update_data(self, index: list[int], changes: list[dict]):
        """Atualiza os dados no banco de dados local de action plan.

        Args:
            index (list[int]): Índices das linhas a serem atualizadas.
            changes (list[dict]): Dicionários com as alterações a serem
                aplicadas em cada linha.

        Raises:
            ValueError: Se algum índice for inválido.
            TypeError: Se algum índice não for inteiro ou se a lista de
                alterações for vazia.
            KeyError: Se alguma chave nos dicionários de alterações for
                inválida.
        """

        try:
            for i, key in enumerate(index):
                key = int(key)
                values = dict(changes[i])
                self.__action_plan_model.update_data(key, values)
        except (ValueError, TypeError, KeyError) as e:
            print(f"An error occurred: {e}")

    def delete_data(self, index: list[int]):
        """Deleta dados no banco de dados local de action plan.

        Args:
            index (list[int]): Índices das linhas a serem deletadas.

        Raises:
            ValueError: Se algum índice for inválido.
            TypeError: Se algum índice não for inteiro.
            KeyError: Se algum índice for inexistente.
        """
        try:
            for i in index:
                i = int(i)
                self.__action_plan_model.delete_data(i)
        except (ValueError, TypeError, KeyError) as e:
            print(f"An error occurred: {e}")
