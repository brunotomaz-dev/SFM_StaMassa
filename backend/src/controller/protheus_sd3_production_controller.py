"""Este módulo controla os dados da tabela SD3."""

import pandas as pd

# pylint: disable=import-error
from src.service.protheus_sd3_production_service import ProtheusSD3ProductionService


class ProtheusSD3ProductionController:
    """Classe para controlar os dados da tabela SD3."""

    def __init__(self) -> None:
        self.__protheus_sd3_production_service = ProtheusSD3ProductionService()

    def get_sd3_data(self, week: bool) -> pd.DataFrame:
        """Retorna os dados da tabela SD3."""

        if week:
            return self.__protheus_sd3_production_service.get_data_production_week()
        return self.__protheus_sd3_production_service.get_data()
