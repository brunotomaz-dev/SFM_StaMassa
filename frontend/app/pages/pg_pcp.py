import asyncio

import pandas as pd
import streamlit as st

# pylint: disable=E0401
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       Requisição de API
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# Função geral para obter os dados da API
async def get_data(url: str, start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """
    Obtém os dados da API.
    """
    url = f"{url}?start={start}&end={end}" if start and end else url
    data = await get_api_data(url)
    return data

# Teste de dados
async def get_all_data() -> tuple:
    urls = [
        APIUrl.URL_MASSA.value,
        APIUrl.URL_PASTA.value,
        APIUrl.URL_MASSA_WEEK.value,
        APIUrl.URL_PASTA_WEEK.value,
    ]
    tasks = [get_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    massa = results[0]
    pasta = results[1]
    massa_week = results[2]
    pasta_week = results[3]
    return massa, pasta, massa_week, pasta_week

@st.cache_data(show_spinner="Obtendo dados", ttl=6000)
def get_df():
    massa, pasta, massa_week, pasta_week = asyncio.run(get_all_data())
    return massa, pasta, massa_week, pasta_week

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                            Sidebar
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

df_massa, df_pasta, df_massa_week, df_pasta_week = get_df()

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
st.title("PCP")

st.write(df_massa)
st.write(df_pasta)