""" Módulo de serviço para tabela sd3 do Protheus."""

import pandas as pd
from src.helpers.variables import PAO_POR_BANDEJA

# pylint: disable=import-error
from src.model.protheus_sd3_production_model import ProtheusSD3ProductionModel


class ProtheusSD3ProductionService:
    """Classe de serviço para tabela sd3 do Protheus."""

    def __init__(self) -> None:
        self.__protheus_sd3_production = ProtheusSD3ProductionModel()
        self.pao_por_bandeja = PAO_POR_BANDEJA

    def get_data(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SD3_PRODUCTION."""
        data = self.__protheus_sd3_production.get_data()

        # Remover espaços vazios na string de PRODUTO
        data["PRODUTO"] = data["PRODUTO"].str.strip()

        return data

    def get_data_production_week(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SD3_PRODUCTION agrupados por semana."""
        df = self.get_data()

        # Remover colunas que não serão necessárias
        df = df.drop(columns=["MAQUINA", "UNIDADE", "LOTE", "USUARIO"])

        # Renomear colunas
        df = df.rename(columns={"QTD": "Caixas"})

        # Multiplicar por 10 que é o número de bandejas por caixa
        df["Bandejas"] = df["Caixas"] * 10

        # Transformar em pão
        df["Pães"] = df["Bandejas"] * df["PRODUTO"].map(self.pao_por_bandeja)

        # Agrupar por datas e produtos
        df = (
            df.groupby(["FABRICA", "PRODUTO", "EMISSAO"])[["Caixas", "Bandejas", "Pães"]]
            .sum()
            .reset_index()
        )

        # Ajustar o formato da coluna de datas
        df["EMISSAO"] = pd.to_datetime(df["EMISSAO"], format="%Y%m%d")

        # Nova coluna com o dia da semana ajustado para 1º dia ser domingo
        df["Data_Semana"] = (df["EMISSAO"].dt.weekday + 1) % 7

        # Ajustar o formato da coluna de datas
        df["Data_Semana"] = df["EMISSAO"] - pd.to_timedelta(df["Data_Semana"], unit="d")

        # Agrupar por datas e produtos
        df = (
            df.groupby(
                [
                    df["Data_Semana"].dt.isocalendar().year,
                    df["Data_Semana"].dt.isocalendar().week,
                    "Data_Semana",
                    "PRODUTO",
                    "FABRICA",
                ]
            )[["Caixas", "Bandejas", "Pães"]]
            .sum()
            .reset_index()
        )

        # Renomear colunas
        df = df.rename(
            columns={
                "Data_Semana": "Data Inicial",
                "PRODUTO": "Produto",
                "FABRICA": "Fábrica",
                "week": "Semana",
                "year": "Ano",
            }
        )

        # Pães para inteiros
        df["Pães"] = df["Pães"].astype(int)

        return df
