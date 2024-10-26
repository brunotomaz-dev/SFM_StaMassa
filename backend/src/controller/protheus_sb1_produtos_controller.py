"""Módulo de Controle para tabela de produtos do Protheus."""

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.protheus_sb1_produtos_service import ProtheusSB1ProdutosService


class ProtheusSB1ProdutosController:
    """Classe de Controle para tabela de produtos do Protheus."""

    def __init__(self) -> None:
        self.__protheus_sb1_produtos_service = ProtheusSB1ProdutosService()

    def get_data(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SB1_PRODUTOS."""
        data = self.__protheus_sb1_produtos_service.get_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
