""" Dados ao Vivo das Máquinas"""

import asyncio
from datetime import datetime

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl
from app.functions.get_date import GetDate
from app.functions.indicators_playground import IndicatorsPlayground

ind_play = IndicatorsPlayground()
get_date = GetDate()

# ================================================================================================ #
#                                         REQUISIÇÃO DE API                                        #
# ================================================================================================ #


async def get_data() -> tuple:
    """
    Obtém os dados da API.
    """
    date_now = datetime.now()
    now_ = date_now.strftime("%Y-%m-%d")
    urls = [
        APIUrl.URL_INFO_IHM.value,
        APIUrl.URL_PROD.value,
        f"{APIUrl.URL_MAQ_INFO.value}?start={now_}&end={now_}",
        f"{APIUrl.URL_MAQ_QUALIDADE.value}?start={now_}&end={now_}",
        APIUrl.URL_EFF.value,
        APIUrl.URL_PERF.value,
        APIUrl.URL_REP.value,
        APIUrl.URL_HIST_IND.value,
    ]
    tasks = [get_api_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    i_ihm = results[0]
    production = results[1]
    maq_info = results[2]
    qual = results[3]
    eff = results[4]
    perf = results[5]
    rep = results[6]
    hist = results[7]
    return i_ihm, production, maq_info, qual, eff, perf, rep, hist


@st.cache_data(show_spinner="Carregando dados de qualidade...", ttl=60)
def get_df() -> tuple:
    ihm, production_, info_, qual, eff, perf, rep, hist = asyncio.run(get_data())
    return ihm, production_, info_, qual, eff, perf, rep, hist


info_ihm, prod, info, quality, eficiencia, performance, reparo, history = get_df()

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

st.subheader("Produção")
st.write(prod)

st.subheader("Qualidade")
st.write(quality)

st.subheader("Info")
st.write(info)
