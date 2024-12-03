"""Rotas de dados vindos das máquinas."""

# ==================================================================================== Importações #
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.controller.maquina_ihm_controller import MaquinaIHMController
from src.controller.maquina_info_controller import MaquinaInfoController
from src.controller.maquina_qualidade_controller import MaquinaQualidadeController
from src.model.error_response import ErrorResponse

# ===================================================================================== Instâncias #
machine_router = APIRouter()

maquina_ihm_controller = MaquinaIHMController()
maquina_info_controller = MaquinaInfoController()
maquina_qualidade_controller = MaquinaQualidadeController()

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
                            "type": "server_error",
                        }
                    ]
                }
            }
        },
    },
)

description_404 = dict(
    {
        "model": ErrorResponse,
        "content": {"application/json": {"example": {"message": "Data not found."}}},
    },
)


# ========================================================================================== Rotas #
@machine_router.get(
    "/maquina_ihm",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
    summary="Retorna os dados da máquina IHM no intervalo de datas especificado.",
)
def get_maquina_ihm(
    start: str = Query(..., description="Data de início no formato %Y-%m-%d"),
    end: str = Query(..., description="Data de fim no formato %Y-%m-%d"),
) -> JSONResponse:
    """Retorna os dados da máquina IHM no intervalo de datas especificado.

    Args:
    start (str): Data de início no formato %Y-%m-%d.
    end (str): Data de fim no formato %Y-%m-%d.

    Returns:
    JSONResponse: Dados da máquina IHM no intervalo de datas especificado.
    """
    try:
        return maquina_ihm_controller.get_data((start, end))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@machine_router.get(
    "/maquina_info",
    summary="Retorna os dados da máquina info no intervalo de datas especificado.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_maquina_info(
    start: str = Query(..., description="Data de início no formato %Y-%m-%d"),
    end: str = Query(..., description="Data de fim no formato %Y-%m-%d"),
) -> JSONResponse:
    """Retorna os dados da máquina info no intervalo de datas especificado.

    Args:
    start (str): Data de início no formato %Y-%m-%d.
    end (str): Data de fim no formato %Y-%m-%d.

    Returns:
    JSONResponse: Dados da máquina info no intervalo de datas especificado.
    """
    try:
        return maquina_info_controller.get_data((start, end))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@machine_router.get(
    "/maquina_qualidade",
    summary="Retorna os dados da máquina qualidade no intervalo de datas especificado.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_maquina_qualidade(
    start: str = Query(..., description="Data de início no formato %Y-%m-%d"),
    end: str = Query(..., description="Data de fim no formato %Y-%m-%d"),
) -> JSONResponse:
    """Retorna os dados da máquina qualidade no intervalo de datas especificado.

    Args:
    start (str): Data de início no formato %Y-%m-%d.
    end (str): Data de fim no formato %Y-%m-%d.

    Returns:
    JSONResponse: Dados da máquina qualidade no intervalo de datas especificado.
    """
    try:
        return maquina_qualidade_controller.get_data((start, end))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@machine_router.get(
    "/production",
    summary="Retorna os dados de produção da data especificada.",
    responses={
        404: {"description": "Data not found", **description_404},
        500: {"description": "Internal Server Error", **description_500},
    },
)
def get_production(
    day: str = Query(..., description="Data de início no formato %Y-%m-%d")
) -> JSONResponse:
    """Retorna os dados de produção da data especificada.

    Returns:
    JSONResponse: Dados de produção da data especificada.
    """
    try:
        return maquina_info_controller.get_production_data_by_day(day)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e
