import asyncio

import pandas as pd
import streamlit as st

from ..api.requests_ import fetch_api_data
from ..api.urls import APIUrl
from ..helpers.variables import CICLOS_ESPERADOS, CICLOS_ESPERADOS_BOL


async def get_data(url: str) -> pd.DataFrame:
    """Função que faz a requisição assíncrona dos dados da API."""
    data = await fetch_api_data(url)
    return pd.DataFrame(data)


@st.cache_data(ttl=60 * 60)
def cycle_data():
    """
    Função que retorna os dados de ciclo.
    """
    maq_info_cycles = asyncio.run(get_data(APIUrl.URL_MAQ_INFO_CYCLE.value))
    return maq_info_cycles


def calcular_perda_ciclo(
    ciclos_reais: int | float, tempo_rodando: int | float, ciclos_esperados: int | float
) -> int:
    """
    Função que calcula a perda de ciclo.
    """
    if ciclos_reais == 0:
        return 0

    ciclos_feitos = ciclos_reais * tempo_rodando
    ciclos = ciclos_esperados * tempo_rodando

    if ciclos_reais < ciclos_esperados:
        return int((ciclos - ciclos_feitos) / ciclos_esperados)
    return 0


def performance_ciclo(
    dataframe: pd.DataFrame, dt_inicio: str, dt_fim: str, turn_choice: str, line_choice: list[str]
) -> tuple:
    """
    Função que calcula perda de tempo relacionado a ciclo abaixo do esperado.
    Exemplo: O ciclo por minuto esperado: 11.3, mas o ciclo real é 10.5.
    O ciclo real é 10.5, então a perda de ciclo é 0.8 ciclo por minuto.
    Se a cada 60 segundos eu deveria fazer 11.3 ciclos, em um turno de 8 horas
    (11.3 * 60 * 8), eu deveria fazer 5424, mas fiz 5040, então a perda de ciclo
    é de 384 ciclos.
    Em tempo de produção, a perda de ciclo é de 36 minutos. Em % de perda, é 7.08%.
    """

    # Novo dataframe com apenas a data, linha, turno e maquina_id
    df_lines = (
        dataframe[["data_registro", "linha", "turno", "maquina_id", "tempo", "status"]]
        .drop_duplicates()
        .copy()
        .reset_index(drop=True)
    )

    maq_info_cycles = cycle_data()

    # Ajustar a data para o formato correto
    maq_info_cycles["data_registro"] = pd.to_datetime(maq_info_cycles["data_registro"])
    maq_info_cycles["data_registro"] = maq_info_cycles["data_registro"].dt.date

    # Filtra por data
    maq_info_cycles = maq_info_cycles[
        (maq_info_cycles["data_registro"] >= dt_inicio)
        & (maq_info_cycles["data_registro"] <= dt_fim)
    ]

    # Unir os dados
    maq_info_cycles = maq_info_cycles.merge(
        df_lines, on=["data_registro", "turno", "maquina_id"], how="left"
    )

    # Remove onde a linha é nula
    maq_info_cycles = maq_info_cycles[maq_info_cycles["linha"].notnull()]

    # Filtrar por linha
    maq_info_cycles = maq_info_cycles[maq_info_cycles["linha"].isin(line_choice)]

    # Filtrar por turno
    maq_info_cycles = (
        maq_info_cycles[maq_info_cycles["turno"] == turn_choice] if turn_choice else maq_info_cycles
    )

    # Filtrar o maq_info_cycles para manter apenas o produto que contém "BOL " no nome
    maq_info_bol = maq_info_cycles[maq_info_cycles["produto"].str.contains(" BOL")]
    maq_info_bag = maq_info_cycles[~maq_info_cycles["produto"].str.contains(" BOL")]

    # Fazer a média dos ciclos
    maq_info_cycles_bol = (
        maq_info_bol["media_ciclo"].mean().round(2) if not maq_info_bol.empty else 0
    )
    maq_info_cycles_bag = maq_info_bag["media_ciclo"].mean().round(2)

    # Manter apenas as linhas onde o status é rodando
    time_bol = maq_info_bol[maq_info_bol["status"] == "rodando"]["tempo"].sum()
    time_bag = maq_info_bag[maq_info_bag["status"] == "rodando"]["tempo"].sum()

    # Calcular a perda de ciclo
    perda_ciclo_bag = calcular_perda_ciclo(maq_info_cycles_bag, time_bag, CICLOS_ESPERADOS)
    perda_ciclo_bol = calcular_perda_ciclo(maq_info_cycles_bol, time_bol, CICLOS_ESPERADOS_BOL)

    perda = perda_ciclo_bag + perda_ciclo_bol
    perda_maq = pd.concat(
        [
            perda_por_linha(maq_info_bol, CICLOS_ESPERADOS_BOL),
            perda_por_linha(maq_info_bag, CICLOS_ESPERADOS),
        ]
    )

    return perda, perda_maq


def perda_por_linha(df: pd.DataFrame, ciclos_esperados: int | float) -> pd.DataFrame:
    """
    Função que calcula a perda de ciclo por linha.
    """
    df = df.copy()
    df = df[df["status"] == "rodando"]

    df_g = (
        df.groupby(["linha"])
        .agg(media_ciclo=("media_ciclo", "mean"), tempo=("tempo", "sum"))
        .reset_index()
    )

    # Calcular a perda de ciclo
    df_g["perda_ciclo"] = df_g.apply(
        lambda x: calcular_perda_ciclo(x["media_ciclo"], x["tempo"], ciclos_esperados), axis=1
    )

    # Agrupar por linha
    perda_ciclo = df_g.groupby("linha")["perda_ciclo"].sum().reset_index()

    # Renomear as colunas
    perda_ciclo.columns = ["causa", "tempo"]

    # Ajustar causa (que agora é numero da linha ex.: 2) para o nome da linha (ex.: Linha 2)
    perda_ciclo["causa"] = perda_ciclo["causa"].apply(lambda x: f"Linha {int(x)}")

    # Ordenar por tempo
    perda_ciclo = perda_ciclo.sort_values(by="tempo", ascending=False)

    # Manter apenas os 5 primeiros
    perda_ciclo = perda_ciclo.head(5).reset_index(drop=True)

    return perda_ciclo
