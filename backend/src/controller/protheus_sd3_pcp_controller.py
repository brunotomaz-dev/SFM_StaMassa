""" Este módulo é responsável por controlar os dados da tabela SD3. """

import pandas as pd

# pylint: disable=import-error
from src.service.protheus_sd3_pcp_service import ProtheusSD3PCPService


class ProtheusSD3PCPController:
    """Classe para controlar os dados da tabela SD3."""

    def __init__(self) -> None:
        self.__protheus_sd3_pcp_service = ProtheusSD3PCPService()

    def get_sd3_data(self, start: str, end: str) -> pd.DataFrame:
        """Retorna os dados da tabela SD3."""
        return self.__protheus_sd3_pcp_service.get_data(start, end)
