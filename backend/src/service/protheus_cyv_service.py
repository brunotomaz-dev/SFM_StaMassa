"""Módulo de serviço para o DB Protheus CYV."""

import pandas as pd
from src.helpers.variables import (
    RENDIMENTO_BOLINHA,
    RENDIMENTO_BOLINHA_ATUALIZADO,
    RENDIMENTO_CHEIA,
    RENDIMENTO_REPROCESSO,
)

# pylint: disable=import-error
from src.model.protheus_cyv_model import ProtheusCYVModel
from src.service.functions.clean_pcp_data import CleanPCPData


class ProtheusCYVService:

    def __init__(self) -> None:
        self.__protheus_cyv_model = ProtheusCYVModel()
        self.__clean = CleanPCPData()

    def get_massa_data(self) -> pd.DataFrame:
        """Realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_CYV."""
        data = self.__protheus_cyv_model.get_massa_data()

        if not data.empty:
            data = self.__clean.clean_massa(data)
            data = self.__massa_sum(data)

        return data

    def get_massa_week_data(self) -> pd.DataFrame:
        """Realiza a consulta no banco de dados e retorna os dados por semana."""

        data = self.__protheus_cyv_model.get_massa_data()

        if not data.empty:
            data = self.__clean.clean_massa(data)
            data = self.__massa_sum(data)
            data = self.__massa_week_sum(data)

        return data

    def get_pasta_data(self) -> pd.DataFrame:
        """Realiza a consulta no banco de dados e retorna os dados da tabela PROTHEUS_CYV."""
        data = self.__protheus_cyv_model.get_pasta_data()

        if not data.empty:
            data = self.__clean.clean_pasta(data)
            data = self.__pasta_adj(data)

        return data

    def get_pasta_week_data(self) -> pd.DataFrame:
        """Realiza a consulta no banco de dados e retorna os dados por semana."""
        data = self.__protheus_cyv_model.get_pasta_data()

        if not data.empty:
            data = self.__clean.clean_pasta(data)
            data = self.__pasta_adj(data)
            data = self.__pasta_week_sum(data)

        return data

    @staticmethod
    def __massa_sum(df: pd.DataFrame) -> pd.DataFrame:
        """
        Soma a massa de cada tipo e calcula o total de pães produzidos.

        Parameters
        ----------
        df: pd.DataFrame
            Dataframe com os dados de massa.

        Returns
        -------
        pd.DataFrame
            Dataframe com as informações de massa somadas e calculadas.
        """

        # Soma a massa de cada tipo
        df = (
            df.groupby(["Data_Registro", "Turno", "Fabrica"])
            .agg(
                Qtd_Batidas_Cheias=("Batidas_Cheia", "sum"),
                Peso_Batidas_Cheias=("Peso_Massa_BC", "sum"),
                Qtd_Batidas_Reprocesso=("Batidas_Reprocesso", "sum"),
                Peso_Batidas_Reprocesso=("Peso_Massa_BR", "sum"),
                Qtd_Batidas_Bolinha=("Batidas_Bolinha", "sum"),
                Peso_Batidas_Bolinha=("Peso_Massa_BB", "sum"),
            )
            .reset_index()
        )

        # Cálculo de pães baguete produzidos
        df["Baguete_Total"] = (
            df["Qtd_Batidas_Cheias"] * RENDIMENTO_CHEIA
            + df["Qtd_Batidas_Reprocesso"] * RENDIMENTO_REPROCESSO
        )

        # Ajusta a data
        df["Data_Registro"] = pd.to_datetime(df["Data_Registro"])
        # Data de corte para ajuste na batida de bolinha
        data_corte = pd.to_datetime("2024-08-05")

        # Inicializa a coluna de Bolinha
        df["Bolinha_Total"] = 0

        # Cálculo de pães bolinha produzidos - peso e rendimento antigos
        df.loc[df["Data_Registro"] < data_corte, "Bolinha_Total"] = (
            df["Qtd_Batidas_Bolinha"] * RENDIMENTO_BOLINHA
        )

        # Cálculo de pães bolinha produzidos - peso e rendimento atualizados
        df.loc[df["Data_Registro"] >= data_corte, "Bolinha_Total"] = (
            df["Qtd_Batidas_Bolinha"] * RENDIMENTO_BOLINHA_ATUALIZADO
        )

        # Ajustando colunas de quantidade para int
        cols = [
            "Qtd_Batidas_Cheias",
            "Qtd_Batidas_Reprocesso",
            "Qtd_Batidas_Bolinha",
            "Baguete_Total",
            "Bolinha_Total",
        ]

        df[cols] = df[cols].astype(int)

        return df

    @staticmethod
    def __massa_week_sum(df: pd.DataFrame) -> pd.DataFrame:
        """
        Função que soma os dados de massa por semana e retorna uma nova tabela.

        Ajusta o dia da semana para que a semana comece na segunda-feira.
        Cria uma nova coluna com a data da semana.
        Realiza a soma dos dados por semana, turno e fábrica.

        Retorna:
        - DataFrame: Tabela com os dados de massa por semana.
        """
        df = df.copy()

        # Ajustar o dia da semana
        df["Dia_Semana"] = df["Data_Registro"].dt.weekday
        df["Dia_Semana"] = (df["Dia_Semana"] + 1) % 7

        # Cria uma nova coluna com a data da semana
        df["Data_Semana"] = df["Data_Registro"] - pd.to_timedelta(df["Dia_Semana"], unit="d")

        # Criar uma nova tabela com dados agrupados por semana
        df = (
            df.groupby(
                [
                    df["Data_Semana"].dt.isocalendar().year,
                    df["Data_Semana"].dt.isocalendar().week,
                    "Data_Semana",
                    "Turno",
                    "Fabrica",
                ]
            )
            .agg(
                Qtd_Batidas_Cheias=("Qtd_Batidas_Cheias", "sum"),
                Peso_Batidas_Cheias=("Peso_Batidas_Cheias", "sum"),
                Qtd_Batidas_Reprocesso=("Qtd_Batidas_Reprocesso", "sum"),
                Peso_Batidas_Reprocesso=("Peso_Batidas_Reprocesso", "sum"),
                Qtd_Batidas_Bolinha=("Qtd_Batidas_Bolinha", "sum"),
                Peso_Batidas_Bolinha=("Peso_Batidas_Bolinha", "sum"),
                Baguete_Total=("Baguete_Total", "sum"),
                Bolinha_Total=("Bolinha_Total", "sum"),
            )
            .reset_index()
        )

        return df

    @staticmethod
    def __pasta_adj(df: pd.DataFrame) -> pd.DataFrame:
        """Ajusta os dados de pasta para o formato correto."""
        # Remove o espaço em branco no produto
        df["Produto"] = df["Produto"].str.strip()

        # Substitui o espaço por underline
        df["Produto"] = df["Produto"].str.replace(" ", "_")

        # Cria colunas auxiliares para criar pivot table
        df["Produto_Batidas"] = df["Produto"].str.title() + "_Batidas"
        df["Produto_Peso"] = df["Produto"].str.title() + "_Peso"

        # Criar pivot de batidas
        df_batidas = df.pivot_table(
            index=["Data_Registro", "Turno", "Fabrica"],
            columns="Produto_Batidas",
            values="Batidas_Pasta",
            aggfunc="sum",
            fill_value=0,
        )

        # Criar pivot de peso
        df_peso = df.pivot_table(
            index=["Data_Registro", "Turno", "Fabrica"],
            columns="Produto_Peso",
            values="Peso_Pasta",
            aggfunc="sum",
            fill_value=0,
        )

        # Unir as duas tabelas
        df = pd.concat([df_batidas, df_peso], axis=1).reset_index()

        # Reordenar as colunas
        df = df[
            [
                "Data_Registro",
                "Turno",
                "Fabrica",
                "Tradicional_Batidas",
                "Tradicional_Peso",
                "Picante_Batidas",
                "Picante_Peso",
                "Cebola_Batidas",
                "Cebola_Peso",
                "Pasta_Doce_Batidas",
                "Pasta_Doce_Peso",
            ]
        ]

        return df

    @staticmethod
    def __pasta_week_sum(df: pd.DataFrame) -> pd.DataFrame:
        """Função que soma os dados de pasta por semana e retorna uma nova tabela."""

        df = df.copy()

        # Ajustar o dia da semana
        df["Dia_Semana"] = df["Data_Registro"].dt.weekday
        df["Dia_Semana"] = (df["Dia_Semana"] + 1) % 7

        # Cria uma nova coluna com a data da semana
        df["Data_Semana"] = df["Data_Registro"] - pd.to_timedelta(df["Dia_Semana"], unit="d")

        # Criar uma nova tabela com dados agrupados por semana
        df = (
            df.groupby(
                [
                    df["Data_Semana"].dt.isocalendar().year,
                    df["Data_Semana"].dt.isocalendar().week,
                    "Data_Semana",
                    "Turno",
                    "Fabrica",
                ]
            )
            .agg(
                Tradicional_Batidas=("Tradicional_Batidas", "sum"),
                Tradicional_Peso=("Tradicional_Peso", "sum"),
                Picante_Batidas=("Picante_Batidas", "sum"),
                Picante_Peso=("Picante_Peso", "sum"),
                Cebola_Batidas=("Cebola_Batidas", "sum"),
                Cebola_Peso=("Cebola_Peso", "sum"),
                Doce_Batidas=("Pasta_Doce_Batidas", "sum"),
                Doce_Peso=("Pasta_Doce_Peso", "sum"),
            )
            .reset_index()
        )

        return df
