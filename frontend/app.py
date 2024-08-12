""" Arquivo principal da aplicação Streamlit. """

import numpy as np
import streamlit as st

# pylint: disable=import-error
from pages.api.requests_ import get_api_data
from pages.api.urls import APIUrl
from pages.functions.get_date import get_this_month

# ================================================================================================ #
#                                         REQUISIÇÃO DE API                                        #
# ================================================================================================ #


def get_data(url, start, end):
    """Obtém os dados da API."""
    url = f"{url}?start={start}&end={end}"
    data = get_api_data(url)
    return data


@st.cache_data(show_spinner="Carregando dados...", ttl=60)
def get_ihm_data(start: str | None = None, end: str | None = None):
    """Obtém os dados da máquina IHM."""
    if start is None and end is None:
        start, end = get_this_month()

    data = get_data(APIUrl.URL_MAQ_IHM.value, start, end)

    # Ajuste na coluna os_numero
    data.os_numero = data.os_numero.astype(str).str.zfill(6)
    data.os_numero = np.where(data.os_numero == "000000", None, data.os_numero)

    # Ajuste na coluna de operador_id
    data.operador_id = data.operador_id.astype(str).str.zfill(6)
    data.operador_id = np.where(data.operador_id == "000000", None, data.operador_id)

    return data


@st.cache_data(show_spinner="Carregando dados...", ttl=60)
def get_info_data(start: str | None = None, end: str | None = None):
    """Obtém os dados da máquina Info."""
    if start is None and end is None:
        start, end = get_this_month()

    return get_data(APIUrl.URL_MAQ_INFO.value, start, end)


@st.cache_data(show_spinner="Carregando dados...", ttl=60)
def get_quality_data(start: str | None = None, end: str | None = None):
    """Obtém os dados da máquina Qualidade."""
    if start is None and end is None:
        start, end = get_this_month()

    data = get_data(APIUrl.URL_MAQ_QUALIDADE.value, start, end)

    # Ajustar medidas
    data.descarte_paes = data.descarte_paes.apply(
        lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    data.descarte_paes_pasta = data.descarte_paes_pasta.apply(
        lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    data.descarte_pasta = data.descarte_pasta.apply(
        lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    return data


@st.cache_data(show_spinner="Carregando dados...", ttl=60)
def get_production_data(start: str | None = None, end: str | None = None):
    """Obtém os dados de produção da máquina Info."""
    if start is None and end is None:
        start, end = get_this_month()

    return get_data(APIUrl.URL_MAQ_PROD.value, start, end)


# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #
maquina_ihm = get_ihm_data()
maquina_info = get_info_data()
maquina_quality = get_quality_data()
maquina_production = get_production_data()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

st.title("Teste de API")
st.write("Dados da máquina IHM:")
st.write(maquina_ihm)
print(maquina_ihm)
st.write("Dados da máquina Info:")
st.write(maquina_info)
st.write("Dados da máquina Qualidade:")
st.write(maquina_quality)
st.write("Dados de produção da máquina Info:")
st.write(maquina_production)
