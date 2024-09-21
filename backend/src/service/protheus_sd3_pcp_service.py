"""Módulo de serviço para tabela sd3 do Protheus."""

import pandas as pd

# pylint: disable=import-error
from src.model.protheus_sd3_pcp_model import ProtheusSD3PCPModel


class ProtheusSD3PCPService:
    """Classe de serviço para tabela sd3 do Protheus."""

    def __init__(self) -> None:
        self.__protheus_sd3_pcp = ProtheusSD3PCPModel()

    def get_data(self, start: str, end: str) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SD3_PCP."""

        data = self.__protheus_sd3_pcp.get_data(start, end)

        # Remover espaços vazios na string de PRODUTO
        data["descricao"] = data["descricao"].str.strip()

        return data
