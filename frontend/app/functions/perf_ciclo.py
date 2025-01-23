import asyncio

import pandas as pd
import streamlit as st
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl


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
        dataframe[["data_registro", "linha", "turno", "maquina_id"]]
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

    # Manter apenas as linhas onde o status é rodando
    df = dataframe[dataframe["status"] == "rodando"]

    # Filtrar o maq_info_cycles para manter apenas o produto que contém "BOL " no nome
    maq_info_cycles_bol = maq_info_cycles[maq_info_cycles["produto"].str.contains(" BOL")]
    maq_info_cycles_bag = maq_info_cycles[~maq_info_cycles["produto"].str.contains(" BOL")]

    # Fazer a média dos ciclos
    maq_info_cycles_bol = maq_info_cycles_bol["media_ciclo"].mean().round(2)
    maq_info_cycles_bag = maq_info_cycles_bag["media_ciclo"].mean().round(2)

    # Calcular o tempo total rodando
    tempo_total = df["tempo"].sum()

    return maq_info_cycles_bag, maq_info_cycles_bol
