"""Módulo responsável por ajustar os dados para os dataframes de heatmap."""

import numpy as np
import pandas as pd

# pylint: disable=import-error
from app.functions.get_date import get_this_month
from app.helpers.variables import TURNOS, IndicatorType


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

        return df_ind

    def create_all_dates_df(self, turno: bool, fab: int) -> pd.DataFrame:
        """Cria um dataframe com todas as datas do mês."""
        # Todas datas do mês em formato de string (YYYY-MM-DD)
        all_dates = pd.date_range(start=self.__start, end=self.__end, freq="D").strftime("%Y-%m-%d")

        r_lines = {
            0: range(1, 15),
            1: range(1, 10),
            2: range(10, 15),
        }[fab]

        tile_line = {
            0: 14,
            1: 9,
            2: 5,
        }[fab]

        if turno:
            # Repetir as datas para cada turno
            turnos = TURNOS * len(all_dates)
            df = pd.DataFrame({"data_registro": np.tile(all_dates, 3), "turno": turnos})
        else:
            # Repetir as datas para cada linha
            linhas = list(r_lines) * len(all_dates)
            df = pd.DataFrame({"data_registro": np.tile(all_dates, tile_line), "linha": linhas})

        return df

    def get_indicator(
        self,
        df: pd.DataFrame,
        indicator: IndicatorType,
        turn: str | None,
        line_turn: str,
        fabrica: str,
    ) -> pd.DataFrame:
        """Obtém o indicador."""
        # Ajustar os dados básicos
        df = self.__basic_adjust(df.copy(), indicator)

        # Verificar se o usuário escolheu linha ou turno
        is_turn = line_turn == "Turno"

        # Confirma que há seleção válida de turno
        selected_turn = not is_turn and turn in TURNOS

        # Fabrica
        fabrica = {
            "Todas as Fábricas": 0,
            "Fábrica 1": 1,
            "Fábrica 2": 2,
        }[fabrica]

        # Criar um dataframe com todas as datas do mês
        df_dates = self.create_all_dates_df(is_turn, fabrica)

        # Filtra caso seja selecionado um turno
        df = df[df.turno == turn] if selected_turn else df

        # Filtra caso seja selecionado uma fábrica
        df = df[df.fabrica == fabrica] if fabrica != 0 else df

        # Garantir o formato da data
        df.data_registro = pd.to_datetime(df.data_registro).dt.strftime("%Y-%m-%d")
        df_dates.data_registro = pd.to_datetime(df_dates.data_registro).dt.strftime("%Y-%m-%d")

        # Agrupa o dataframe por data e pela escolha do usuário
        df = (
            df.groupby(["data_registro", "turno" if is_turn else "linha"], observed=False)
            .agg({indicator.value: "mean"})
            .round(2)
            .reset_index()
        )

        # Merge dos dataframes por data e pela escolha do usuário
        df = pd.merge(
            df_dates, df, on=["data_registro", "turno" if is_turn else "linha"], how="left"
        )

        return df

    def create_heatmap_structure(self, df: pd.DataFrame, indicator: IndicatorType) -> pd.DataFrame:
        """Ajusta os dados dos indicadores para uso no Heatmap - Cartesian Chart."""
        # Verificar dados para saber se estão organizados por linha ou turno

        # Pega o indicador
        df_ind = df.copy()

        # Arredondar o indicador e deixar sem casas decimais
        df_ind[indicator.value] = df_ind[indicator.value].round(0)

        # Identificar a coluna escolhida pelo usuário
        c_col = "turno" if "turno" in df_ind.columns else "linha"

        # Se houver a coluna linha, seus valores precisam ser convertidos para string
        if c_col == "linha":
            df_ind[c_col] = df_ind[c_col].astype(str)

        # Ajusta para "-"" os valores nulos, necessário para o heatmap
        df_ind[indicator.value] = df_ind[indicator.value].fillna("-")

        # Deixa a data de registro apenas com o dia
        df_ind.data_registro = pd.to_datetime(df_ind.data_registro).dt.strftime("%d")

        # Mapear ('turno ou linha') e data_registro para índices numéricos
        data_to_idx = {x: j for j, x in enumerate(df_ind.data_registro.unique())}
        choice_to_idx = {y: i for i, y in enumerate(df_ind[c_col].unique())}

        # Criando a estrutura de dados para o heatmap
        data = [
            [
                data_to_idx[row.data_registro],
                choice_to_idx[row[c_col]],
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
