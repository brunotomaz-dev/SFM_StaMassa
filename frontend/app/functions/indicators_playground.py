"""Módulo responsável por ajustar os dados para os dataframes de heatmap."""

import numpy as np
import pandas as pd

# pylint: disable=import-error
from app.functions.get_date import get_this_month
from app.helpers.variables import IndicatorType


class IndicatorsPlayground:
    """Classe responsável por trabalhar com os indicadores."""

    def __init__(self) -> None:
        self.__start, self.__end = get_this_month()

    @staticmethod
    def __basic_adjust(df_ind: pd.DataFrame, indicator: IndicatorType) -> pd.DataFrame:
        """Ajusta os dados básicos."""

        # Indicador (performance, eficiencia, reparo)
        indicator = indicator.value

        # Ajustar o indicador para  X%
        df_ind[indicator] = df_ind[indicator] * 100

        # Corrigir erros possíveis limitando a 0 min e 120 max
        df_ind[indicator] = df_ind[indicator].clip(0, 120)

    def create_all_dates_df(
        self, turno: bool | None = None, linha: bool | None = None
    ) -> pd.DataFrame:
        """Cria um dataframe com todas as datas do mês."""
        # Todas datas do mês em formato de string (YYYY-MM-DD)
        all_dates = pd.date_range(start=self.__start, end=self.__end, freq="D").strftime("%Y-%m-%d")

        if turno and not linha:
            # Repetir as datas para cada turno
            turnos = [
                "NOT",
                "MAT",
                "VES",
            ] * len(all_dates)
            df = pd.DataFrame({"data_registro": np.tile(all_dates, 3), "turno": turnos})
        elif linha and not turno:
            # Repetir as datas para cada linha
            linhas = range(1, 14) * len(all_dates)
            df = pd.DataFrame({"data_registro": np.tile(all_dates, 14), "linha": linhas})

        return df

    def get_indicator(
        self,
        df: pd.DataFrame,
        indicator: IndicatorType,
        turno: bool | None = None,
        linha: bool | None = None,
    ) -> pd.DataFrame:
        """Obtém o indicador."""
        # Ajustar os dados básicos
        df = self.__basic_adjust(df, indicator)

        # Se linha e turno forem None, retorna o dataframe ajustado para turno
        if not linha and not turno:
            turno = True

        # Se linha e turno forem True, retorna o dataframe ajustado para turno
        if linha and turno:
            turno = True

        # Criar um dataframe com todas as datas do mês
        df_dates = self.create_all_dates_df(turno, linha)

        # Agrupa o dataframe por data e pela escolha do usuário
        df = (
            df.groupby(["data_registro", "turno" if turno else "linha"], observed=False)
            .agg({indicator.value: "mean"})
            .round(2)
            .reset_index()
        )

        # Merge dos dataframes por data e pela escolha do usuário
        df = pd.merge(df_dates, df, on=["data_registro", "turno" if turno else "linha"], how="left")

        return df

    def create_heatmap_structure(self, df: pd.DataFrame, indicator: IndicatorType) -> pd.DataFrame:
        """Ajusta os dados dos indicadores para uso no Heatmap - Cartesian Chart."""
        # Verificar dados para saber se estão organizados por linha ou turno

        # Pega o indicador
        df_ind = self.get_indicator(df, indicator)

        # Ajusta para "-"" os valores nulos, necessário para o heatmap
        df_ind[indicator.value] = df_ind[indicator.value].fillna("-")

        # Deixa a data de registro apenas com o dia
        df_ind["data_registro"] = pd.to_datetime(df_ind["data_registro"]).dt.day

        # Mapear ('turno ou linha') e data_registro para índices numéricos
        choice_to_idx = {y: i for i, y in enumerate(df_ind["turno" if turno else "linha"].unique())}
        data_to_idx = {x: j for j, x in enumerate(df_ind["data_registro"].unique())}

        # Criando a estrutura de dados para o heatmap
        data = [
            [
                data_to_idx[row["data_registro"]],
                choice_to_idx[row["turno" if turno else "linha"]],
                row[indicator.value],
            ]
            for _, row in df_ind.iterrows()
        ]

        # Ajustando a estrutura de dados para o heatmap
        data = [[d[0], d[1], d[2]] for d in data]  # acrescentaria um if d[2] != "-" aqui,
        # se não fosse necessário manter os valores nulos para o heatmap

        # Criando listas de dias e turnos/linhas
        days = list(data_to_idx.keys())
        choices = list(choice_to_idx.keys())

        return data, days, choices
