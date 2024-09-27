"""Módulo que gerencia as requisições da API."""

from io import StringIO

import aiohttp
import pandas as pd
import streamlit as st


async def fetch_api_data(url: str) -> pd.DataFrame:
    """
    Obtém os dados da API.
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                df = pd.read_json(StringIO(str(data)), orient="split")
                return df
            else:
                st.error("Erro ao obter os dados da API.")
                return pd.DataFrame()
