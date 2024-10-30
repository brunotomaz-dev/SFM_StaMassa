""" Rota da Api da tabela PROTHEUS_SB2. """

# ==================================================================================== Importações #
from fastapi import APIRouter, HTTPException

# pylint: disable=import-error
from src.controller.protheus_sb2_estoque_controller import ProtheusSB2EstoqueController
from src.model.error_response import ErrorResponse

# ===================================================================================== Instâncias #

protheus_sb2_router = APIRouter()
protheus_sb2_controller = ProtheusSB2EstoqueController()

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


@protheus_sb2_router.get(
    "/caixas_estoque",
    summary="Retorna os dados de Estoque.",
    responses={500: description_500, 404: description_404},
)
def get_protheus_sb2() -> dict:
    """
    Retorna os dados de Estoque de Caixas na Câmara Fria coletados pelo Protheus.
    """

    try:
        return protheus_sb2_controller.get_data()
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
