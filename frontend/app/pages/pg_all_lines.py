"""Página de visão das linhas."""

from datetime import datetime

import pandas as pd
import streamlit as st

# pylint: disable=E0401
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl
from app.components.sfm_gauge_opt2 import create_gauge_chart
from app.functions.get_date import GetDate
from app.helpers.variables import ColorsSTM, IndicatorType

get_date = GetDate()

# Receber a data e turno atual
today, turn = get_date.get_this_turn()


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       Requisição de Api
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


def get_data(url: str, start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """
    Obtém os dados da API.
    """
    url = f"{url}?start={start}&end={end}" if start and end else url
    data = get_api_data(url)
    return data


@st.cache_data(show_spinner="Carregando eficiência...", ttl=60)
def get_eff_ind() -> pd.DataFrame:
    """
    Obtém os dados de eficiência das linhas.
    """
    return get_data(APIUrl.URL_EFF.value)


@st.cache_data(show_spinner="Carregando dados das linhas...", ttl=60)
def get_maq_info() -> pd.DataFrame:
    """
    Obtém os dados de eficiência das linhas.
    """
    return get_data(APIUrl.URL_INFO_IHM.value)


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                          Nav Widgets
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

turn_opt: str
line: int

turns = {
    "NOT": ["NOT"],
    "MAT": ["MAT", "NOT"],
    "VES": ["VES", "MAT", "NOT"],
}[turn]

lines = list(range(1, 15))

turn_opt = st.sidebar.selectbox(
    "Selecione a opção de visualização:", ("Dia Atual", *turns), index=1
)

line = st.sidebar.selectbox("Selecione a linha:", lines, index=0)

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

df_eff = get_eff_ind()
df_maq_info_original = get_maq_info()

# ════════════════════════════════════════════════════════════════ Ajustar O Dataframe De Info ══ #

# Garantir que a data é um pandas Timestamp só com a data
df_maq_info_original.data_registro = pd.to_datetime(df_maq_info_original.data_registro).dt.date
df_eff.data_registro = pd.to_datetime(df_eff.data_registro).dt.date

# Filtrar pelo turno atual e data
df_maq_info_original = df_maq_info_original[(df_maq_info_original.data_registro == today)]
df_eff = df_eff[(df_eff.data_registro == today)]
df_maq_info = df_maq_info_original.copy()
if turn_opt != "Dia Atual":
    df_maq_info = df_maq_info[(df_maq_info.turno == turn_opt)]
    df_eff = df_eff[(df_eff.turno == turn_opt)]

# Filtrar pela linha
df_maq_info = df_maq_info[(df_maq_info.linha == line)].reset_index(drop=True)
df_maq_info_original = df_maq_info_original[(df_maq_info_original.linha == line)].reset_index(
    drop=True
)
df_eff = df_eff[(df_eff.linha == line)].reset_index(drop=True)

eff_value = round(df_eff.eficiencia.mean() * 100)

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

st.title(f"Linha: {str(line)}")
st.subheader(f"Máquina: {df_eff.maquina_id.iloc[0]}")

r1_col1, r1_col2, r1_col3, r1_col4, r1_col5 = st.columns(5)

with r1_col1:
    _, turno_atual = get_date.get_this_turn()
    df_maq_info_status = df_maq_info_original[(df_maq_info_original.turno == turno_atual)]
    # Recuperar o status da última entrada de maq_info
    with st.container():
        status = df_maq_info_status.status.iloc[-1].capitalize()
        back_color = ColorsSTM.GREEN.value if status == "Rodando" else ColorsSTM.RED.value
        opt_1 = f"background-color: {back_color}; color: {ColorsSTM.LIGHT_GREY.value};"
        st.markdown(
            """
        <style>
            .card {
                text-align: center;
                font-size: 2vw;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                height: 100%;
                """
            + opt_1
            + """
                }
        </style>
        <div class="card">"""
            + f"""{status}</div>""",
            unsafe_allow_html=True,
        )
    if status != "Rodando":
        with st.container():
            causa = df_maq_info_status.causa.iloc[-1]
            causa = causa if causa else "Não informado"
            st.markdown(
                """
                <style>
                    .card2 {
                        text-align: center;
                        font-size: 1vw;
                        background-color: #fff;
                        padding: 10px;
                        margin-top: 20px;
                        border: 1px solid #ddd;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        height: 100%;
                        }
                </style>
                <div class="card2">"""
                + f"""{causa}</div>""",
                unsafe_allow_html=True,
            )
        with st.container():
            # Hora da Parada
            hora_inicial = df_maq_info_status.data_hora.iloc[-1]
            # Hora atual
            hora_final = datetime.now()
            # Ajustar para pd.Datetime
            hora_inicial = pd.to_datetime(hora_inicial)
            # Converter para pd.Datetime
            hora_final = pd.to_datetime(hora_final)
            # Calcular o tempo de parada em minutos
            tempo = round((hora_final - hora_inicial).seconds / 60)
            # Ajustar tempo para uma string formatada no formato mm
            tempo = str(tempo).replace(".", ",")

            st.markdown(
                """<div class="card2" style="font-size: 1.5vw;">""" + f"""{tempo} min</div>""",
                unsafe_allow_html=True,
            )


with r1_col2:
    create_gauge_chart(IndicatorType.EFFICIENCY, eff_value, "line_gg_eff", True)


st.write(df_eff)
st.write(df_maq_info)
