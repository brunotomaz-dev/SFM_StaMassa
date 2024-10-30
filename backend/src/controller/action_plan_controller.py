""" Módulo de Controle de action_plan """

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse
from src.service.action_plan_service import ActionPlanService


class ActionPlanController:
    """Classe para controle dos dados da tabela action_plan do banco de dados local."""

    def __init__(self) -> None:
        self.__action_plan_service = ActionPlanService()

    def get_data(self) -> pd.DataFrame:
        """Obtém os dados da tabela action_plan do banco de dados local."""
        data = self.__action_plan_service.get_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados na tabela action_plan do banco de dados local."""
        try:
            self.__action_plan_service.insert_data(data)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Data inserted successfully."},
            )
        except ValueError as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"An error occurred: {e}"},
            )

    def update_data(self, index: list[int], changes: list[dict]) -> None:
        """Atualiza os dados na tabela action_plan do banco de dados local.

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
            self.__action_plan_service.update_data(index, changes)
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"message": "Data updated successfully."}
            )
        except (ValueError, TypeError, KeyError) as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"An error occurred: {e}"},
            )

    def delete_data(self, index: list[int]) -> None:
        """Deleta dados na tabela action_plan do banco de dados local.

        Args:
            index (list[int]): Índices das linhas a serem deletadas.

        Raises:
            ValueError: Se algum índice for inválido.
            TypeError: Se algum índice não for inteiro.
            KeyError: Se algum índice for inexistente.
        """
        try:
            self.__action_plan_service.delete_data(index)
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"message": "Data deleted successfully."}
            )
        except (ValueError, TypeError, KeyError) as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"An error occurred: {e}"},
            )
