"""Módulo que limpa e organiza os dados do protheus para uso do pcp."""

from datetime import time

import pandas as pd

# pylint: disable=import-error
from src.helpers.variables import (
    MASSADA_BOLINHA,
    MASSADA_BOLINHA_ATUALIZADA,
    MASSADA_CHEIA,
    MASSADA_REPROCESSO,
)


class CleanPCPData:
    """Classe que realiza a limpeza e organiza os dados do protheus para uso do pcp."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def __get_shift(hour_time: time) -> str:
        """
        Retorna o turno do dia em que o horário especificado ocorre.

        Parameters
        ----------
        hour_time : time
            Horário em que o turno deve ser verificado.

        Returns
        -------
        str
            O turno do dia em que o horário especificado ocorre. Pode ser
            MAT (matutino), VES (vespertino) ou NOT (não identificado).
        """

        # Início dos turnos
        mat_begin = time(8, 0, 0)
        ves_begin = time(16, 0, 0)
        ves_end = time(23, 59, 59)

        # Identificar os turnos pelo horário
        if mat_begin <= hour_time > ves_begin:
            return "MAT"
        elif ves_begin <= hour_time > ves_end:
            return "VES"
        else:
            return "NOT"

    @staticmethod
    def __mass_adjustment(data: pd.DataFrame, position: int = None) -> pd.DataFrame:
        """
        Ajusta as colunas de batidas e peso de massa cheia
        para as colunas de batidas e peso de massa reprocesso/bolinha.

        Parameters
        ----------
        data: pd.DataFrame
            DataFrame com os dados a serem ajustados.
        position: int, optional
            Posição da coluna de batidas e peso de massa a serem renomeadas.
            Deve ser 1 para reprocesso e 2 para bolinha.

        Returns
        -------
        pd.DataFrame
            DataFrame com as colunas de batidas e peso de massa.
        """
        df_massadas = (
            data.groupby(
                ["Codigo_Maquina", "Descricao_Maquina", "Data_Registro", "Turno", "Fabrica"]
            )
            .agg(
                Usuario_Registro=("Usuario_Registro", "first"),
                Batidas_Cheia=("Quantidade_Atropelamento", "count"),
                Peso_Massa_BC=("Quantidade_Atropelamento", "sum"),
            )
            .reset_index()
        )

        # Dicionario para escolher o nome da coluna de forma dinâmica
        columns_opt = {
            1: {
                "Batidas_Cheia": "Batidas_Reprocesso",
                "Peso_Massa_BC": "Peso_Massa_BR",
            },
            2: {
                "Batidas_Cheia": "Batidas_Bolinha",
                "Peso_Massa_BC": "Peso_Massa_BB",
            },
        }

        # Renomear colunas conforme posição escolhida
        if position is not None:
            df_massadas = df_massadas.rename(columns=columns_opt[position])

        return df_massadas

    def clean_massa(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajusta a hora de registro, separa os dados em 3 partes (massa cheia, reprocesso e bolinha),
        soma os valores de batidas de reprocesso e bolinha, e une os dados.
        """

        # Ajustar a hora de registro
        df["Hora_Registro"] = pd.to_datetime(df["Hora_Registro"], format="%H:%M:%S").dt.time

        # Criar coluna de turno
        df["Turno"] = df["Hora_Registro"].apply(self.__get_shift)

        # Separando o dataframe em partes conforme atropelamento
        df_cheia = df[df["Quantidade_Atropelamento"] == MASSADA_CHEIA]
        df_reprocesso = df[df["Quantidade_Atropelamento"] == MASSADA_REPROCESSO]
        df_bolinha = df[
            (df["Quantidade_Atropelamento"] == MASSADA_BOLINHA)
            | (df["Quantidade_Atropelamento"] == MASSADA_BOLINHA_ATUALIZADA)
        ]

        # Soma de valores de batidas de reprocesso e bolinha
        df_cheia = self.__mass_adjustment(df_cheia)
        df_reprocesso = self.__mass_adjustment(df_reprocesso, 1)
        df_bolinha = self.__mass_adjustment(df_bolinha, 2)

        # Unir dataframe de massa e reprocesso
        df_massadas = df_cheia.merge(
            df_reprocesso,
            how="outer",
            on=[
                "Codigo_Maquina",
                "Descricao_Maquina",
                "Data_Registro",
                "Turno",
                "Fabrica",
                "Usuario_Registro",
            ],
        )

        # Unir dataframe de massa e bolinha
        df_massadas = df_massadas.merge(
            df_bolinha,
            how="outer",
            on=[
                "Codigo_Maquina",
                "Descricao_Maquina",
                "Data_Registro",
                "Turno",
                "Fabrica",
                "Usuario_Registro",
            ],
        )

        # Ajustar a data de registro
        df_massadas["Data_Registro"] = pd.to_datetime(df_massadas["Data_Registro"], format="%Y%m%d")

        return df_massadas

    def clean_pasta(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajusta os dados de pasta."""

        # Ajustar a hora de registro
        df["Hora_Registro"] = pd.to_datetime(df["Hora_Registro"], format="%H:%M:%S").dt.time

        # Criar coluna de turno
        df["Turno"] = df["Hora_Registro"].apply(self.__get_shift)

        # Agrega somando valores
        df = (
            df.groupby(
                [
                    "Codigo_Maquina",
                    "Descricao_Maquina",
                    "Data_Registro",
                    "Turno",
                    "Fabrica",
                    "Produto",
                ]
            )
            .agg(
                Usuario_Registro=("Usuario_Registro", "first"),
                Batidas_Pasta=("Quantidade_Atropelamento", "count"),
                Peso_Pasta=("Quantidade_Atropelamento", "sum"),
            )
            .reset_index()
        )

        # Ajustar a data de registro
        df["Data_Registro"] = pd.to_datetime(df["Data_Registro"], format="%Y%m%d")

        return df
