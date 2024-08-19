"""Página de indicadores de eficiência, performance e reparo."""

import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import IndicatorType

ind_play = IndicatorsPlayground()

# ================================================================================================ #
#                                         REQUISIÇÃO DE API                                        #
# ================================================================================================ #


def get_data(url: str, start: str | None = None, end: str | None = None) -> dict:
    """Obtém os dados da API."""
    url = f"{url}?start={start}&end={end}" if start and end else url
    data = get_api_data(url)
    return data


@st.cache_data(show_spinner="Carregando dados do indicadores...", ttl=60)
def get_indicators_data() -> tuple:
    """Obtém os dados dos indicadores."""

    eff = get_data(APIUrl.URL_EFF.value)
    perf = get_data(APIUrl.URL_PERF.value)
    rep = get_data(APIUrl.URL_REP.value)

    return eff, perf, rep


@st.cache_data(show_spinner="Carregando dados do histórico indicadores...", ttl=600)
def get_history_data() -> dict:
    """Obtém os dados do histórico dos indicadores."""

    return get_data(APIUrl.URL_HIST_IND.value)


# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #
eficiencia, performance, reparo = get_indicators_data()
history_ind = get_history_data()

# ==================================== Ajustes Dos Indicadores =================================== #
df_eff = ind_play.get_indicator(eficiencia, IndicatorType.EFFICIENCY)
df_perf = ind_play.get_indicator(performance, IndicatorType.PERFORMANCE)
df_rep = ind_play.get_indicator(reparo, IndicatorType.REPAIR)

# Heatmap


# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

st.title("Shop Floor Management!")

st.write(df_eff)
st.write(df_perf)
st.write(df_rep)
