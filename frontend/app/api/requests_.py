"""Módulo que gerencia as requisições da API."""

from io import StringIO

import pandas as pd
import requests
import streamlit as st


def get_api_data(url: str) -> pd.DataFrame:
    """
    Obtém os dados da API.
    """

    response = requests.get(url, timeout=40)
    if response.status_code == 200:
        data = response.json()
        df = pd.read_json(StringIO(str(data)), orient="split")
        return df
    else:
        st.error("Erro ao obter os dados da API.")
        return pd.DataFrame()
