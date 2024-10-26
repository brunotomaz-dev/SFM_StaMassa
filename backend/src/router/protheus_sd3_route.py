""" Rota da API da tabela PROTHEUS_SD3. """

# ==================================================================================== Importações #

from fastapi import APIRouter, HTTPException, Query
from src.controller.protheus_sd3_pcp_controller import ProtheusSD3PCPController

# pylint: disable=import-error
from src.controller.protheus_sd3_production_controller import ProtheusSD3ProductionController
from src.model.error_response import ErrorResponse

# ===================================================================================== Instâncias #

protheus_sd3_router = APIRouter()
protheus_sd3_production_controller = ProtheusSD3ProductionController()
protheus_sd3_pcp_controller = ProtheusSD3PCPController()

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


@protheus_sd3_router.get(
    "/production",
    summary="Retorna os dados de Produção por Semana/Produto.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_sd3_production() -> dict:
    """
    Retorna os dados de Produção coletados pelo Protheus.
    """

    try:
        return protheus_sd3_production_controller.get_sd3_data(True)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[
                {
                    "loc": ["query", "start"],
                    "msg": "Erro interno do servidor.",
                    "type": "server_error",
                }
            ],
        ) from e


@protheus_sd3_router.get(
    "/pcp_estoque",
    summary="Retorna os dados de Ajuste de Estoque.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_sd3_pcp(
    start: str = Query(..., description="Data de início no formato %Y%m%d"),
    end: str = Query(..., description="Data de fim no formato %Y-%m-%d"),
) -> dict:
    """
    Retorna os dados de Ajuste de Estoque coletados pelo Protheus.
    """

    try:
        return protheus_sd3_pcp_controller.get_sd3_data(start, end)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[
                {
                    "loc": ["query", "start"],
                    "msg": "Erro interno do servidor.",
                    "type": "server_error",
                }
            ],
        ) from e
