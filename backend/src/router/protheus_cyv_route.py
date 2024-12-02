""" Rota da API da tabela PROTHEUS_CYV. """

# ==================================================================================== Importações #
from fastapi import APIRouter, HTTPException

# pylint: disable=import-error
from src.controller.protheus_cyv_controller import ProtheusCYVController
from src.model.error_response import ErrorResponse

# ===================================================================================== Instâncias #

protheus_cyv_router = APIRouter()
protheus_cyv_controller = ProtheusCYVController()

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


@protheus_cyv_router.get(
    "/massa",
    summary="Retorna os dados de Massa.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_cyv() -> dict:
    """
    Retorna os dados de Massa coletados pelo Protheus.
    """

    try:
        return protheus_cyv_controller.get_massa_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@protheus_cyv_router.get(
    "/massa_week",
    summary="Retorna os dados de Massa por semana.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_cyv_week() -> dict:
    """
    Retorna os dados de Massa por semana coletados pelo Protheus.
    """

    try:
        return protheus_cyv_controller.get_massa_week_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@protheus_cyv_router.get(
    "/pasta",
    summary="Retorna os dados de CYV Pasta.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_cyv_pasta() -> dict:
    """
    Retorna os dados de CYV Pasta coletados pelo Protheus.
    """

    try:
        return protheus_cyv_controller.get_pasta_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@protheus_cyv_router.get(
    "/pasta_week",
    summary="Retorna os dados de CYV Pasta por semana.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_cyv_pasta_week() -> dict:
    """
    Retorna os dados de CYV Pasta por semana coletados pelo Protheus.
    """

    try:
        return protheus_cyv_controller.get_pasta_week_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e


@protheus_cyv_router.get(
    "/cart_entering_greenhouse",
    summary="Retorna os dados de entrada de carrinhos na estufa.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_cyv_cart_entering_greenhouse() -> dict:
    """
    Retorna os dados de entrada de carrinhos na estufa coletados pelo Protheus.
    """

    try:
        return protheus_cyv_controller.get_cart_entering_greenhouse()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["query", "start"], "msg": str(e), "type": "server_error"}],
        ) from e
