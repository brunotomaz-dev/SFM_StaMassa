""" Rotas de dados vindos do DB local. """

# ==================================================================================== Importações #
from typing import List

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from src.controller.action_plan_controller import ActionPlanController

# pylint: disable=import-error
from src.controller.efficiency_controller import EfficiencyController
from src.controller.historic_ind_controller import HistoricIndController
from src.controller.info_ihm_controller import InfoIHMController
from src.controller.performance_controller import PerformanceController
from src.controller.production_controller import ProductionController
from src.controller.reparo_controller import ReparoController
from src.model.error_response import ErrorResponse

# ===================================================================================== Instâncias #
local_router = APIRouter()

production_controller = ProductionController()
info_ihm_controller = InfoIHMController()
efficiency_controller = EfficiencyController()
performance_controller = PerformanceController()
reparo_controller = ReparoController()
historic_ind_controller = HistoricIndController()
action_plan_controller = ActionPlanController()

# =========================================================================== Documentação De Erro #
description_500 = dict(
    {
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["query", "start"],
                            "msg": "Erro interno do servidor.",
                            "type": "value_error",
                        }
                    ]
                }
            }
        },
    }
)

description_404 = dict(
    {
        "model": ErrorResponse,
        "content": {"application/json": {"example": {"message": "Data not found."}}},
    },
)

description_400 = dict(
    {
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "message": "An error occurred: {e}",
                }
            }
        },
    }
)


# ======================================================================================== Modelos #
class ActionPlanData(BaseModel):
    """Modelo de dados para inserção na tabela action_plan do DB local."""

    Data: str
    Indicador: str
    Dias_em_Aberto: int
    Prioridade: int
    Descricao_do_Problema: str
    Impacto: float
    Causa_Raiz: str
    Contencao: str
    Solucao: str
    Feedback: str
    Responsavel: str
    Conclusao: bool


class ActionPlanUpdate(BaseModel):
    """Modelo de dados para atualização na tabela action_plan do DB local."""

    index: list[int]
    changes: list[dict]


class ActionPlanDelete(BaseModel):
    """Modelo de dados para deleção na tabela action_plan do DB local."""

    index: list[int]


# ========================================================================================== Rotas #


@local_router.get(
    "/production",
    summary="Retorna os dados de produção do DB local - mês corrente.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_production() -> JSONResponse:
    """Retorna os dados de produção do DB local - mês corrente.

    Returns:
    JSONResponse: Dados de produção do DB local - mês corrente.
    """
    try:
        return production_controller.get_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.get(
    "/info_ihm",
    summary="Retorna os dados de info_ihm do DB local - mês corrente.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_info_ihm() -> JSONResponse:
    """Retorna os dados de info_ihm do DB local - mês corrente.

    Returns:
    JSONResponse: Dados de info_ihm do DB local - mês corrente.
    """
    try:
        return info_ihm_controller.get_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.get(
    "/efficiency",
    summary="Retorna os dados de eficiência do DB local - mês corrente.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_efficiency() -> JSONResponse:
    """Retorna os dados de eficiência do DB local - mês corrente.

    Returns:
    JSONResponse: Dados de eficiência do DB local - mês corrente.
    """
    try:
        return efficiency_controller.get_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.get(
    "/performance",
    summary="Retorna os dados de performance do DB local - mês corrente.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_performance() -> JSONResponse:
    """Retorna os dados de performance do DB local - mês corrente.

    Returns:
    JSONResponse: Dados de performance do DB local - mês corrente.
    """
    try:
        return performance_controller.get_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.get(
    "/reparo",
    summary="Retorna os dados de reparo do DB local - mês corrente.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_reparo() -> JSONResponse:
    """Retorna os dados de reparo do DB local - mês corrente.

    Returns:
    JSONResponse: Dados de reparo do DB local - mês corrente.
    """
    try:
        return reparo_controller.get_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.get(
    "/historic_ind",
    summary="Retorna os dados de historic_ind do DB local - mês corrente.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_historic_ind() -> JSONResponse:
    """Retorna os dados de historic_ind do DB local.

    Returns:
    JSONResponse: Dados de historic_ind do DB local.
    """
    try:
        return historic_ind_controller.get_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.get(
    "/action_plan",
    summary="Retorna os dados de action_plan do DB local.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_action_plan() -> JSONResponse:
    """Retorna os dados de action_plan do DB local.

    Returns:
    JSONResponse: Dados de action_plan do DB local.
    """
    try:
        return action_plan_controller.get_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.post(
    "/action_plan",
    summary="Insere dados na tabela action_plan do DB local.",
    responses={
        400: {"description": "Bad Request", **description_400},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def insert_action_plan(data: List[ActionPlanData]) -> JSONResponse:
    """Insere dados na tabela action_plan do DB local.

    Args:
        data (List[ActionPlanData]): Dados a serem inseridos na tabela action_plan.

    Returns:
        JSONResponse: Mensagem de sucesso ou erro.
    """
    dataframe = pd.DataFrame([d.model_dump() for d in data])

    try:
        return action_plan_controller.insert_data(dataframe)
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=e.errors(),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.put(
    "/action_plan",
    summary="Atualiza os dados na tabela action_plan do DB local.",
    responses={
        400: {"description": "Bad Request", **description_400},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def update_action_plan(data: ActionPlanUpdate) -> JSONResponse:
    """Atualiza os dados na tabela action_plan do DB local.

    Args:
        data (dict): Dados a serem atualizados na tabela action_plan.

    Returns:
    JSONResponse: Mensagem de sucesso ou erro.
    """
    try:
        return action_plan_controller.update_data(data.index, data.changes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@local_router.delete(
    "/action_plan",
    summary="Deleta dados na tabela action_plan do DB local.",
    responses={
        400: {"description": "Bad Request", **description_400},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def delete_action_plan(data: ActionPlanDelete) -> JSONResponse:
    """Deleta dados na tabela action_plan do DB local.

    Args:
        data (dict): Dados a serem deletados na tabela action_plan.

    Returns:
    JSONResponse: Mensagem de sucesso ou erro.
    """
    try:
        return action_plan_controller.delete_data(data.index)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e
