""" Rota da Api da tabela PROTHEUS_SB1. """

# ==================================================================================== Importações #
from fastapi import APIRouter, HTTPException

# pylint: disable=import-error
from src.controller.protheus_sb1_produtos_controller import ProtheusSB1ProdutosController
from src.model.error_response import ErrorResponse

# ===================================================================================== Instâncias #

protheus_sb1_router = APIRouter()
protheus_sb1_controller = ProtheusSB1ProdutosController()

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


@protheus_sb1_router.get(
    "/",
    summary="Retorna os dados de Produtos.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_sb1() -> dict:
    """
    Retorna os dados de Produtos coletados pelo Protheus.
    """

    try:
        return protheus_sb1_controller.get_data()
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
