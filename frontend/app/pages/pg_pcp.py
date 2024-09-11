import pandas as pd
import streamlit as st

# pylint: disable=E0401
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       Requisição de API
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# Função geral para obter os dados da API
def get_data(url: str, start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """
    Obtém os dados da API.
    """
    url = f"{url}?start={start}&end={end}" if start and end else url
    data = get_api_data(url)
    return data

# Dados de Massa
@st.cache_data(show_spinner="Obtendo dados de Massa")
def get_massa_data() -> pd.DataFrame:
    """
    Obter os dados de Massa.
    """
    return get_data(APIUrl.URL_MASSA.value)

# Dados de Pasta
@st.cache_data(show_spinner="Obtendo dados de Pasta")
def get_pasta_data() -> pd.DataFrame:
    """
    Obter os dados de Pasta.
    """
    return get_data(APIUrl.URL_PASTA.value)


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                            Sidebar
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
df_massa = get_massa_data()
df_pasta = get_pasta_data()

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
st.title("PCP")

st.write(df_massa)
st.write(df_pasta)