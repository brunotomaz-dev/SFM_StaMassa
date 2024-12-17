"""Módulo que gerencia as requisições da API."""

import logging
from io import StringIO

import aiohttp
import pandas as pd
import streamlit as st

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


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
                logger.error(
                    "Erro ao obter os dados da API. Status code: %s\n Message: %s\n Url: %s",
                    response.status,
                    response.reason,
                    response.url,
                )

                return pd.DataFrame()


async def insert_api_data(url: str, data: list[dict]) -> None:
    """
    Insere os dados na API.
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 201:
                return
            else:
                error_message = await response.text()
                st.error(f"Erro ao inserir os dados na API: {response.status} - {error_message}")
                print(f"Erro ao inserir os dados na API: {response.status} - {error_message}")


async def delete_api_data(url: str, index: list[int]) -> None:
    """
    Exclui os dados da API.
    """

    async with aiohttp.ClientSession() as session:
        async with session.delete(url, json={"index": index}) as response:
            if response.status == 200:
                return
            else:
                error_message = await response.text()
                st.error(f"Erro ao excluir os dados da API: {response.status} - {error_message}")
                print(f"Erro ao excluir os dados da API: {response.status} - {error_message}")


async def update_api_data(url: str, index: list[int], data: list[dict]) -> None:
    """
    Atualiza os dados na API.
    """

    async with aiohttp.ClientSession() as session:
        async with session.put(url, json={"index": index, "changes": data}) as response:
            if response.status == 200:
                return
            else:
                error_message = await response.text()
                st.error(f"Erro ao atualizar os dados na API: {response.status} - {error_message}")
                print(f"Erro ao atualizar os dados na API: {response.status} - {error_message}")
