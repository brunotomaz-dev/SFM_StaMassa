"""Módulo com funções auxiliares para o projeto."""

import pandas as pd

# pylint: disable=E0401
from app.helpers.variables import PAO_POR_BANDEJA


def adjust_pao(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Funcão para ajustar o pão."""
    # Copia o dataframe
    df = dataframe.copy()

    # Remover colunas que não serão necessárias
    df = df.drop(columns=["MAQUINA", "UNIDADE", "LOTE", "USUARIO"])

    # Renomear colunas
    df = df.rename(columns={"QTD": "Caixas"})

    # Multiplicar por 10 que é o número de bandejas por caixa
    df["Bandejas"] = df["Caixas"] * 10

    # Transformar em pão
    df["Pães"] = df["Bandejas"] * df["PRODUTO"].map(PAO_POR_BANDEJA)

    # Agrupar por datas e produtos
    df = df.groupby(["FABRICA", "PRODUTO", "EMISSAO"])[["Caixas", "Bandejas", "Pães"]].sum().reset_index()

    # Ajustar o formato da coluna de datas
    df["EMISSAO"] = pd.to_datetime(df["EMISSAO"], format="%Y%m%d")

    # Nova coluna com o dia da semana ajustado para 1º dia ser domingo
    df["Data_Semana"] = (df["EMISSAO"].dt.weekday + 1) % 7

    # Ajustar o formato da coluna de datas
    df["Data_Semana"] = df["EMISSAO"] - pd.to_timedelta(df["Data_Semana"], unit="d")

    # Agrupar por datas e produtos
    df = (df.groupby([
        df["Data_Semana"].dt.isocalendar().year,
        df["Data_Semana"].dt.isocalendar().week,
        "Data_Semana",
        "PRODUTO",
        "FABRICA",
    ])[["Caixas", "Bandejas", "Pães"]].sum().reset_index())

    # Renomear colunas
    df = df.rename(columns={
        "Data_Semana": "Data Inicial",
        "PRODUTO": "Produto",
        "FABRICA": "Fábrica",
        "week": "Semana",
        "year": "Ano",
    })

    # Pães para inteiros
    df["Pães"] = df["Pães"].astype(int)

    return df
