"""Página de indicadores de eficiência, performance e reparo."""

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl
from app.components.sfm_gauge import create_gauge_chart
from app.components.sfm_heatmap import create_heatmap_chart
from app.components.sfm_line import create_line_chart
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import TURNOS, IndicatorType

ind_play = IndicatorsPlayground()

# ================================================================================================ #
#                                         REQUISIÇÃO DE API                                        #
# ================================================================================================ #


def get_data(url: str, start: str | None = None, end: str | None = None) -> dict:
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


# ================================================================================================ #
#                                            NAV WIDGETS                                           #
# ================================================================================================ #
# Valores no heatmap
heat_label = st.sidebar.checkbox("Mostrar valores", value=True)

# Selectbox - Seleção de linha ou turno para o heatmap
line_turn = st.sidebar.selectbox("Apresentar por:", ["Turno", "Linha"])

# Selectbox - Seleção de turno para o heatmap
turn: str | None = None
if line_turn == "Linha":
    turn = st.sidebar.selectbox("Selecionar um turno:", ["Todos os Turnos", *TURNOS])

# Selectbox - Seleção de fábrica
fabrica = st.sidebar.selectbox(
    "Selecionar uma fábrica:", ["Todas as Fábricas", "Fábrica 1", "Fábrica 2"]
)

# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #
eficiencia, performance, reparo = get_indicators_data()
history_ind = get_history_data()

# ==================================== Ajustes Dos Indicadores =================================== #
df_eff = ind_play.get_indicator(eficiencia, IndicatorType.EFFICIENCY, turn, line_turn, fabrica)
df_perf = ind_play.get_indicator(performance, IndicatorType.PERFORMANCE, turn, line_turn, fabrica)
df_rep = ind_play.get_indicator(reparo, IndicatorType.REPAIR, turn, line_turn, fabrica)

# Heatmap - Ajuste dos dataframes para o a estrutura cartesiana para o heatmap
df_eff_opt, days_eff, ref_eff = ind_play.create_heatmap_structure(
    df_eff.copy(), IndicatorType.EFFICIENCY
)
df_perf_opt, days_perf, ref_perf = ind_play.create_heatmap_structure(
    df_perf.copy(), IndicatorType.PERFORMANCE
)
df_rep_opt, days_rep, ref_rep = ind_play.create_heatmap_structure(
    df_rep.copy(), IndicatorType.REPAIR
)

# Gauge - Valores dos indicadores do mês corrente
efficiency_actual = round(df_eff.eficiencia.dropna().mean())
performance_actual = round(df_perf.performance.dropna().mean())
repair_actual = round(df_rep.reparo.dropna().mean())

# Gauge - Valores dos indicadores do mês anterior
efficiency_last = round(history_ind.iloc[-1][IndicatorType.EFFICIENCY.value] * 100)
performance_last = round(history_ind.iloc[-1][IndicatorType.PERFORMANCE.value] * 100)
repair_last = round(history_ind.iloc[-1][IndicatorType.REPAIR.value] * 100)


# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

st.title("Shop Floor Management")
st.divider()

# ========================================== Eficiência ========================================== #
eff_col1, eff_col2, eff_col3 = st.columns([1, 8, 1])

with eff_col1:
    create_gauge_chart(0, IndicatorType.EFFICIENCY, efficiency_last, "sfm_eff_gauge_last")

with eff_col2:
    create_heatmap_chart(
        df_eff_opt, IndicatorType.EFFICIENCY, days_eff, ref_eff, heat_label, "sfm_eff_heatmap"
    )
    create_line_chart(df_eff, IndicatorType.EFFICIENCY)

with eff_col3:
    create_gauge_chart(1, IndicatorType.EFFICIENCY, efficiency_actual, "sfm_eff_gauge")

# ========================================== Performance ========================================= #
perf_col1, perf_col2, perf_col3 = st.columns([1, 8, 1])

with perf_col1:
    create_gauge_chart(0, IndicatorType.PERFORMANCE, performance_last, "sfm_perf_gauge_last")

with perf_col2:
    create_heatmap_chart(
        df_perf_opt, IndicatorType.PERFORMANCE, days_perf, ref_perf, heat_label, "sfm_perf_heatmap"
    )
    create_line_chart(df_perf, IndicatorType.PERFORMANCE)

with perf_col3:
    create_gauge_chart(1, IndicatorType.PERFORMANCE, performance_actual, "sfm_perf_gauge")

# ============================================ Reparo ============================================ #
rep_col1, rep_col2, rep_col3 = st.columns([1, 8, 1])

with rep_col1:
    create_gauge_chart(0, IndicatorType.REPAIR, repair_last, "sfm_rep_gauge_last")

with rep_col2:
    create_heatmap_chart(
        df_rep_opt, IndicatorType.REPAIR, days_rep, ref_rep, heat_label, "sfm_rep_heatmap"
    )
    create_line_chart(df_rep, IndicatorType.REPAIR)

with rep_col3:
    create_gauge_chart(1, IndicatorType.REPAIR, repair_actual, "sfm_rep_gauge")
