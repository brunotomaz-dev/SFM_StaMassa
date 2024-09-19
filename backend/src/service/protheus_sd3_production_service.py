""" Módulo de serviço para tabela sd3 do Protheus."""
import pandas as pd

# pylint: disable=import-error
from src.model.protheus_sd3_production_model import ProtheusSD3ProductionModel


class ProtheusSD3ProductionService:
    """Classe de serviço para tabela sd3 do Protheus."""

    def __init__(self) -> None:
        self.__protheus_sd3_production = ProtheusSD3ProductionModel()


    def get_data(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SD3_PRODUCTION."""
        data = self.__protheus_sd3_production.get_data()

        # Remover espaços vazios na string de PRODUTO
        data["PRODUTO"] = data["PRODUTO"].str.strip()

        return data
