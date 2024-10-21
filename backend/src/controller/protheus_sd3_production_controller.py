"""Este módulo controla os dados da tabela SD3."""

import pandas as pd
from fastapi import status
from fastapi.responses import JSONResponse

# pylint: disable=import-error
from src.service.protheus_sd3_production_service import ProtheusSD3ProductionService


class ProtheusSD3ProductionController:
    """Classe para controlar os dados da tabela SD3."""

    def __init__(self) -> None:
        self.__protheus_sd3_production_service = ProtheusSD3ProductionService()

    def get_sd3_data(self, week: bool) -> pd.DataFrame:
        """Retorna os dados da tabela SD3."""

        if week:
            data = self.__protheus_sd3_production_service.get_data_production_week()
        else:
            data = self.__protheus_sd3_production_service.get_data()

        if data is None or data.empty:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
            )

        return JSONResponse(content=data.to_json(date_format="iso", orient="split"))
