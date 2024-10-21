"""Módulo de Controle para tabela de estoque do Protheus."""

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.protheus_sb2_estoque_service import ProtheusSB2EstoqueService


class ProtheusSB2EstoqueController:
    """Classe de Controle para tabela de estoque do Protheus."""

    def __init__(self) -> None:
        self.__protheus_sb2_estoque_service = ProtheusSB2EstoqueService()

    def get_data(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SB2_ESTOQUE."""
        data = self.__protheus_sb2_estoque_service.get_data()
        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
