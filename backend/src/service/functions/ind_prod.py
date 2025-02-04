"""Módulo que gera indicadores de eficiência, performance e reparos."""

import numpy as np
import pandas as pd

# pylint: disable=import-error
from src.helpers.variables import (
    AF_REP,
    CICLOS_BOLINHA,
    CICLOS_ESPERADOS,
    DESC_EFF,
    DESC_PERF,
    DESC_REP,
    NOT_EFF,
    NOT_PERF,
    IndicatorType,
)
from src.service.functions.production_times import ProductionTimes


class IndProd:
    """Classe responsável por gerar indicadores de eficiência, performance e reparos."""

    def __init__(self) -> None:
        self.__production_times = ProductionTimes()
        self.desc_eff = DESC_EFF
        self.desc_perf = DESC_PERF
        self.desc_rep = DESC_REP
        self.not_eff = NOT_EFF
        self.not_perf = NOT_PERF
        self.af_rep = AF_REP
        self.ciclos_ideais = CICLOS_ESPERADOS
        self.ciclos_bolinha = CICLOS_BOLINHA

    def get_indicators(
        self, df_info: pd.DataFrame, df_prod: pd.DataFrame, indicator: IndicatorType
    ) -> pd.DataFrame:
        """
        Calcula os indicadores de eficiência, performance e reparos.
        """

        # Pega apenas as paradas
        df_stops = df_info[df_info.status == "parada"]
        df_stops = df_stops.reset_index(drop=True)

        # Dicionário de descontos
        desc_dict = {
            IndicatorType.EFFICIENCY: self.desc_eff,
            IndicatorType.PERFORMANCE: self.desc_perf,
            IndicatorType.REPAIR: self.desc_rep,
        }

        # Dicionário de motivos, problemas e causas que não afetam o indicador
        skip_dict = {
            IndicatorType.EFFICIENCY: self.not_eff,
            IndicatorType.PERFORMANCE: self.not_perf,
            IndicatorType.REPAIR: self.af_rep,
        }

        # Ajuste de parada programada para perf e reparos para ser np.nan - Feito nos ajustes
        paradas_programadas = pd.Series()
        if indicator != IndicatorType.EFFICIENCY:
            mask = (df_stops.causa.isin(["Sem Produção", "Backup", "Programação"])) & (
                df_stops.tempo >= 478
            )
            paradas_programadas = df_stops[mask][["data_registro", "turno", "linha"]]

        # ================================== Calcula O Indicador ================================= #
        # Calcula o tempo de desconto
        df_stops = self.__production_times.get_discount_time(
            df_stops, desc_dict[indicator], skip_dict[indicator], indicator
        )

        # Agrupa para ter o valor total de tempo e de desconto
        df_stops = (
            df_stops.groupby(["maquina_id", "linha", "data_registro", "turno"], observed=False)
            .agg(
                tempo=("tempo", "sum"),
                desconto=("desconto", "sum"),
                excedente=("excedente", "sum"),
            )
            .reset_index()
        )

        # Ajusta a data por garantia
        df_stops.data_registro = pd.to_datetime(df_stops.data_registro)
        df_prod.data_registro = pd.to_datetime(df_prod.data_registro)

        # Une os dois dataframes
        df = pd.merge(
            df_prod,
            df_stops,
            how="left",
            on=["maquina_id", "linha", "data_registro", "turno"],
        )

        # Preenche os valores nulos
        df = df.fillna(0)

        # Nova coluna para o tempo esperado de produção
        df = self.__production_times.get_expected_production_time(df)

        # Dict de funções para ajustes dos indicadores
        adjust_dict = {
            IndicatorType.EFFICIENCY: self.__eff_adjust,
            IndicatorType.PERFORMANCE: self.__adjust,
            IndicatorType.REPAIR: self.__adjust,
        }

        # Ajusta o indicador
        if indicator != IndicatorType.EFFICIENCY:
            df = adjust_dict[indicator](df, indicator, paradas_programadas)
        else:
            df = adjust_dict[indicator](df, indicator)

        # Ajustar a ordem das colunas
        cols_eff = [
            "fabrica",
            "linha",
            "maquina_id",
            "turno",
            "data_registro",
            "hora_registro",
            "tempo",
            "desconto",
            "excedente",
            "tempo_esperado",
            "total_produzido",
            "producao_esperada",
            indicator.value,
        ]

        cols = [
            "fabrica",
            "linha",
            "maquina_id",
            "turno",
            "data_registro",
            "hora_registro",
            "tempo",
            "desconto",
            "excedente",
            "tempo_esperado",
            indicator.value,
        ]

        return df[cols] if indicator != IndicatorType.EFFICIENCY else df[cols_eff]

    def __eff_adjust(self, df: pd.DataFrame, indicator: IndicatorType) -> pd.DataFrame:
        """
        Ajusta o indicador de eficiência.
        """

        # Variável para identificar quando o produto possui a palavra " BOL "
        mask_bolinha = df["produto"].str.contains(" BOL")

        # NOTE: Código que não levava em conta o bolinha
        # Nova coluna para o tempo esperado de produção
        # df["producao_esperada"] = round(((df.tempo_esperado * self.ciclos_ideais) * 2), 0)

        # NOTE: Código ajustado para o bolinha - acompanhar
        # Nova coluna para o tempo esperado de produção
        df["producao_esperada"] = round(
            df["tempo_esperado"] * (self.ciclos_bolinha * 2) * mask_bolinha
            + df["tempo_esperado"] * (self.ciclos_ideais * 2) * ~mask_bolinha,
            0,
        )

        # Coluna de eficiência
        df[indicator.value] = (df.total_produzido / df.producao_esperada).round(3)

        # Corrige os valores nulos ou incorretos
        df[indicator.value] = df[indicator.value].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Ajustar a eficiência para np.nan se produção esperada for 0
        mask = (df.producao_esperada == 0) & (df[indicator.value] == 0)
        df.loc[mask, indicator.value] = np.nan

        # Ajustar eficiência para tempo de produção esperado menor que 10
        mask = df.tempo_esperado < 10
        df.loc[mask, indicator.value] = np.nan
        df.loc[mask, "produção_esperada"] = 0
        df.loc[mask, "tempo_esperado"] = 0

        return df

    def __adjust(
        self, df: pd.DataFrame, indicador: IndicatorType, paradas_programadas: pd.Series
    ) -> pd.DataFrame:
        """
        Ajusta os indicadores de performance e reparos.
        """

        # Coluna do indicador
        df[indicador.value] = (df.excedente / df.tempo_esperado).round(3)

        # Corrige os valores nulos ou incorretos
        df[indicador.value] = df[indicador.value].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Ajuste para paradas programadas
        paradas_programadas["programada"] = 1

        # Garantir que data_registro seja datetime
        paradas_programadas.data_registro = pd.to_datetime(paradas_programadas.data_registro)
        df.data_registro = pd.to_datetime(df.data_registro)

        # Une os dois dataframes
        df = pd.merge(df, paradas_programadas, how="left", on=["data_registro", "turno", "linha"])

        # np.nan para paradas programadas
        mask = df.programada == 1
        df.loc[mask, indicador.value] = np.nan
        df.loc[mask, "tempo_esperado"] = 0

        # Remove a coluna programada
        df = df.drop(columns="programada")

        return df
