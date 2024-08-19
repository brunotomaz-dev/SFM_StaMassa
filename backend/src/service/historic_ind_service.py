""" Módulo de  serviço para o banco de dados local de Histórico de Indicadores."""

import pandas as pd

# pylint: disable=import-error
from src.model.historic_ind_modal import HistoricInd


class HistoricIndService:
    """Classe para manipulação dos dados do banco de dados local de Histórico de Indicadores."""

    def __init__(self) -> None:
        self.__historic_ind_model = HistoricInd()

    def get_data(self) -> pd.DataFrame:
        """Obtém dados do banco de dados local de Histórico de Indicadores."""
        data = self.__historic_ind_model.get_data()

        if data is None:
            return pd.DataFrame(
                columns=[
                    "data_registro",
                    "total_caixas",
                    "eficiencia",
                    "performance",
                    "reparo",
                    "parada_programada",
                ]
            )

        return data

    def insert_data(self, data: pd.DataFrame) -> None:
        """Insere dados no banco de dados local de Histórico de Indicadores."""
        self.__historic_ind_model.insert_data(data)

    def replace_data(self, data: pd.DataFrame) -> None:
        """Substitui dados no banco de dados local de Histórico de Indicadores."""
        self.__historic_ind_model.replace_data(data)
