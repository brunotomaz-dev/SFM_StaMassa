from datetime import datetime

import pandas as pd
import streamlit as st
from app.api.api_request import api_get, api_get_token


def update_api_dj(url: str, params: str = None):
    """
    Faz uma requisição GET para a API Django.

    Args:
        url (str): URL da API.
        params (str, optional): Parâmetros da requisição. Defaults to None.
    """
    token = st.session_state.api_token

    return api_get(url, token=token["access"], params=params)


def get_for_django():
    """
    Coleta dados das APIs Django e atualiza o estado da sessão.

    Args:
        progresso: Um objeto streamlit.empty para exibir o progresso da operação.

    """

    # Gera o token
    st.session_state.api_token = api_get_token("bruno.tomaz", "Br120800")

    # Variável com data de hoje no formato yyyy-mm-dd
    now = datetime.now()
    now_ = now.strftime("%Y-%m-%d")

    req_info_ihm = update_api_dj("http://localhost:8000/api/info_ihm/")
    req_qual_prod = update_api_dj("http://localhost:8000/api/qual_prod/")
    req_maquina_info = update_api_dj(
        "http://localhost:8000/api/maquinainfo/",
        params=f"data_registro={now_}",
    )
    result_django = [
        pd.DataFrame(req_info_ihm),
        pd.DataFrame(req_qual_prod),
        pd.DataFrame(req_maquina_info),
    ]

    keys_django = [
        "info_ihm",
        "produção",
        "maquina_info_today",
    ]

    for key, res in zip(keys_django, result_django):
        if not res.empty:
            st.session_state[key] = res


get_for_django()

st.write(st.session_state.info_ihm)
st.write(st.session_state.produção)
st.write(st.session_state.maquina_info_today)
