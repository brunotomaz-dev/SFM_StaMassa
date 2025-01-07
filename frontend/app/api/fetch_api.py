"""Módulo responsável pelas requisições necessárias ap app."""

import asyncio
from datetime import datetime

import pandas as pd

# pylint: disable=import-error
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl


# Fragmento para atualizar os dados na API sem recarregar a página
async def update_api() -> list[pd.DataFrame]:
    """Função que atualiza os dados na API sem recarregar a página.

    Ela faz uso de requisições assíncronas para obter os dados das
    seguintes API's:

    - Produção
    - Caixas em estoque
    - Eficiência
    - Performance
    - Reparos
    - Informações da IHM
    - Histórico de indicadores
    - Informações da máquina

    Ela retorna uma lista contendo pandas DataFrames com os dados
    obtidos."""

    # Recebendo data de hoje
    date_now = datetime.now()
    now_ = date_now.strftime("%Y-%m-%d")

    # Urls das api's usadas de forma geral no app
    urls = [
        APIUrl.URL_PROD.value,
        APIUrl.URL_CAIXAS_ESTOQUE.value,
        APIUrl.URL_EFF.value,
        APIUrl.URL_PERF.value,
        APIUrl.URL_REP.value,
        APIUrl.URL_INFO_IHM.value,
        APIUrl.URL_HIST_IND.value,
        f"{APIUrl.URL_MAQ_INFO.value}?start={now_}&end={now_}",
        APIUrl.URL_CART_GREENHOUSE.value,
    ]

    # Execução de tasks
    tasks = [fetch_api_data(url) for url in urls]

    # Gather tasks
    result = await asyncio.gather(*tasks)

    return result
