""" Dados ao Vivo das Máquinas"""

import pandas as pd
import streamlit as st
from streamlit_extras.prometheus import streamlit_registry

# pylint: disable=import-error
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl
from app.functions.indicators_playground import IndicatorsPlayground

ind_play = IndicatorsPlayground()

# ================================================================================================ #
#                                         REQUISIÇÃO DE API                                        #
# ================================================================================================ #


def get_data(url: str, start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Obtém os dados da API."""
    url = f"{url}?start={start}&end={end}" if start and end else url
    data = get_api_data(url)
    return data


@st.cache_data(show_spinner="Carregando dados do indicadores...", ttl=600)
def get_indicators_data() -> tuple:
    """Obtém os dados dos indicadores."""

    eff = get_data(APIUrl.URL_EFF.value)
    perf = get_data(APIUrl.URL_PERF.value)
    rep = get_data(APIUrl.URL_REP.value)

    return eff, perf, rep


@st.cache_data(show_spinner="Carregando dados do histórico indicadores...", ttl=6000)
def get_history_data() -> pd.DataFrame:
    """Obtém os dados do histórico dos indicadores."""

    return get_data(APIUrl.URL_HIST_IND.value)

@st.cache_data(show_spinner="Carregando dados das linhas...", ttl=60)
def get_maq_info() -> pd.DataFrame:
    """Obtém os dados de eficiência das linhas."""
    return get_data(APIUrl.URL_INFO_IHM.value)


eficiencia, performance, reparo = get_indicators_data()
history = get_history_data()
info_ihm = get_maq_info()

# Sortear os dados por data, linha e hora
eficiencia = eficiencia.sort_values(by=["data_registro", "linha", "hora_registro"]).reset_index(
    drop=True
)
performance = performance.sort_values(by=["data_registro", "linha", "hora_registro"]).reset_index(
    drop=True
)
reparo = reparo.sort_values(by=["data_registro", "linha", "hora_registro"]).reset_index(drop=True)

# Formatar data para visualização
eficiencia.data_registro = pd.to_datetime(eficiencia.data_registro).dt.strftime("%d/%m")
performance.data_registro = pd.to_datetime(performance.data_registro).dt.strftime("%d/%m")
reparo.data_registro = pd.to_datetime(reparo.data_registro).dt.strftime("%d/%m")

# Formatar hora para visualização
eficiencia.hora_registro = pd.to_datetime(
    eficiencia.hora_registro, format="%H:%M:%S.%f"
).dt.strftime("%H:%M")
performance.hora_registro = pd.to_datetime(
    performance.hora_registro, format="%H:%M:%S.%f"
).dt.strftime("%H:%M")
reparo.hora_registro = pd.to_datetime(reparo.hora_registro, format="%H:%M:%S.%f").dt.strftime(
    "%H:%M"
)

# Formatar indicadores para visualização como str e em %
eficiencia.eficiencia = (eficiencia.eficiencia * 100).round(1).astype(str) + "%"
performance.performance = (performance.performance * 100).round(1).astype(str) + "%"
reparo.reparo = (reparo.reparo * 100).round(1).astype(str) + "%"

# Formata o indicador "nan%" para "-"
eficiencia.eficiencia = eficiencia.eficiencia.replace("nan%", "-")
performance.performance = performance.performance.replace("nan%", "-")
reparo.reparo = reparo.reparo.replace("nan%", "-")

# Ajustar os números para formato brasileiro (de 1,000.00 para 1.000,00)
eficiencia.total_produzido = eficiencia.total_produzido.apply(
    lambda x: f"{x:,.0f}".replace(",", ".")
)
eficiencia.producao_esperada = eficiencia.producao_esperada.apply(
    lambda x: f"{x:,.0f}".replace(",", ".")
)

# Ajustar nomes das colunas
eficiencia.columns = eficiencia.columns.str.replace("_", " ").str.title()
performance.columns = performance.columns.str.replace("_", " ").str.title()
reparo.columns = reparo.columns.str.replace("_", " ").str.title()

# Renomear coluna tempo para tempo de parada
reparo = reparo.rename(
    columns={
        "Tempo": "Tempo Parada",
        "Desconto": "Tempo Descontado",
        "Excedente": "Tempo que Afeta a Produção",
    }
)
eficiencia = eficiencia.rename(
    columns={
        "Tempo": "Tempo Parada",
        "Desconto": "Tempo Descontado",
        "Excedente": "Tempo que Afeta a Produção",
    }
)
performance = performance.rename(
    columns={
        "Tempo": "Tempo Parada",
        "Desconto": "Tempo Descontado",
        "Excedente": "Tempo que Afeta a Produção",
    }
)

st.title("Hello World")

st.subheader("Eficiência")
st.write(eficiencia)

st.subheader("Performance")
st.write(performance)

st.subheader("Reparo")
st.write(reparo)

st.subheader("Histórico")
st.write(history)

st.subheader("Info de Máquina")
st.write(info_ihm)

