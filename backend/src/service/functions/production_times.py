"""Módulo para análise de dados. Calcula tempo de desconto"""

from datetime import datetime

import numpy as np
import pandas as pd

# pylint: disable=import-error
from src.helpers.variables import IndicatorType


class ProductionTimes:
    """Classe para cálculo de tempo de desconto."""

    def __init__(self) -> None:
        pass

    def get_discount_time(
        self,
        df: pd.DataFrame,
        desc_dict: dict[str, int],
        skip_list: list[str],
        indicator: IndicatorType,
    ) -> pd.DataFrame:
        """
        Calcula o tempo de desconto.
        """

        # Cria uma coluna com o tempo de desconto padrão
        df = df.copy()
        df["desconto"] = 0

        # Caso o motivo, problema ou causa não afete o indicador, o desconto é igual a tempo
        mask = df[["motivo", "problema", "causa"]].apply(lambda x: x.isin(skip_list).any(), axis=1)
        df.loc[mask, "desconto"] = 0 if indicator == IndicatorType.REPAIR else df.tempo

        # Cria um dict para indicadores
        indicator_dict = {
            IndicatorType.EFFICIENCY: df,
            IndicatorType.PERFORMANCE: df[~mask],
            IndicatorType.REPAIR: df[mask],
        }

        df = indicator_dict[indicator].reset_index(drop=True)

        # Aplica o desconto de acordo com as colunas "motivo" ou "problema" ou "causa"
        for key, value in desc_dict.items():
            mask = (
                df[["motivo", "problema", "causa"]]
                .apply(lambda x, key=key: x.str.contains(key, case=False, na=False))
                .any(axis=1)
            )
            df.loc[mask, "desconto"] = value

        # Caso o desconto seja maior que o tempo, o desconto deve ser igual ao tempo
        df.loc[:, "desconto"] = df[["desconto", "tempo"]].min(axis=1)

        # Calcula o excedente, sendo o valor mínimo 0
        df.loc[:, "excedente"] = (df.tempo - df.desconto).clip(lower=0)

        return df

    @staticmethod
    def __get_elapsed_time(turno: str) -> int:
        """
        Calcula o tempo decorrido.

        """
        # Agora
        now = datetime.now()

        if turno == "MAT" and 8 <= now.hour < 16:
            elapsed_time = now - datetime(now.year, now.month, now.day, 8, 0, 0)
        elif turno == "VES" and 16 <= now.hour < 24:
            elapsed_time = now - datetime(now.year, now.month, now.day, 16, 0, 0)
        elif turno == "NOT" and 0 <= now.hour < 8:
            elapsed_time = now - datetime(now.year, now.month, now.day, 0, 0, 0)
        else:
            return 480

        return elapsed_time.total_seconds() / 60

    def get_expected_production_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula o tempo esperado de produção.
        """
        df["tempo_esperado"] = df.apply(
            lambda row: (
                np.floor(self.__get_elapsed_time(row.turno) - row.desconto)
                if row.data_registro.date() == pd.to_datetime("today").date()
                else 480 - row.desconto
            ),
            axis=1,
        )

        return df
