"""Página de indicadores de eficiência, performance e reparo."""

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl
from app.components import sfm_gauge as sfm_gg
from app.components import sfm_gauge_opt2 as sfm_gg2
from app.components.sfm_heatmap import create_heatmap_chart
from app.components.sfm_line import create_line_chart
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import TURNOS, ColorsSTM, IndicatorType
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu

ind_play = IndicatorsPlayground()

# ================================== Visualizações - Sub-páginas ================================= #
Sub_opt1 = "Principal"
Sub_opt2 = "Agregada"

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
#                                            MENU WIDGET                                           #
# ================================================================================================ #

with st.sidebar:
    selected_page = option_menu(
        "Visualização",
        [Sub_opt1, Sub_opt2],
        icons=["bi bi-graph-down", "bi bi-bar-chart-line-fill"],
        menu_icon="cast",
        default_index=0,
    )


# ================================================================================================ #
#                                            NAV WIDGETS                                           #
# ================================================================================================ #
turn: str | None = None
fabrica: str | None = "Todas as Fábricas"
line_turn: str | None = "Turno"

# =========================================== Principal ========================================== #
if selected_page == Sub_opt1:
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

# ==================================== Ajustes Dos Indicadores =================================== #
df_eff = ind_play.get_indicator(eficiencia, IndicatorType.EFFICIENCY, turn, line_turn, fabrica)
df_perf = ind_play.get_indicator(performance, IndicatorType.PERFORMANCE, turn, line_turn, fabrica)
df_rep = ind_play.get_indicator(reparo, IndicatorType.REPAIR, turn, line_turn, fabrica)


# Gauge - Valores dos indicadores do mês corrente
efficiency_actual = round(df_eff.eficiencia.dropna().mean())
performance_actual = round(df_perf.performance.dropna().mean())
repair_actual = round(df_rep.reparo.dropna().mean())


if selected_page == Sub_opt1:
    history_ind = get_history_data()

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
    # Gauge - Valores dos indicadores do mês anterior
    efficiency_last = round(history_ind.iloc[-1][IndicatorType.EFFICIENCY.value] * 100)
    performance_last = round(history_ind.iloc[-1][IndicatorType.PERFORMANCE.value] * 100)
    repair_last = round(history_ind.iloc[-1][IndicatorType.REPAIR.value] * 100)


# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

st.title("Shop Floor Management")
st.divider()

# =========================================== Principal ========================================== #
if selected_page == Sub_opt1:

    # ======================================== Eficiência ======================================== #
    eff_col1, eff_col2, eff_col3 = st.columns([1, 8, 1])

    with eff_col1:
        sfm_gg.create_gauge_chart(
            0, IndicatorType.EFFICIENCY, efficiency_last, "sfm_eff_gauge_last"
        )

    with eff_col2:
        create_heatmap_chart(
            df_eff_opt, IndicatorType.EFFICIENCY, days_eff, ref_eff, heat_label, "sfm_eff_heatmap"
        )
        create_line_chart(df_eff, IndicatorType.EFFICIENCY)

    with eff_col3:
        sfm_gg.create_gauge_chart(1, IndicatorType.EFFICIENCY, efficiency_actual, "sfm_eff_gauge")

    # ======================================== Performance ======================================= #
    perf_col1, perf_col2, perf_col3 = st.columns([1, 8, 1])

    with perf_col1:
        sfm_gg.create_gauge_chart(
            0, IndicatorType.PERFORMANCE, performance_last, "sfm_perf_gauge_last"
        )

    with perf_col2:
        create_heatmap_chart(
            df_perf_opt,
            IndicatorType.PERFORMANCE,
            days_perf,
            ref_perf,
            heat_label,
            "sfm_perf_heatmap",
        )
        create_line_chart(df_perf, IndicatorType.PERFORMANCE)

    with perf_col3:
        sfm_gg.create_gauge_chart(
            1, IndicatorType.PERFORMANCE, performance_actual, "sfm_perf_gauge"
        )

    # ========================================== Reparo ========================================== #
    rep_col1, rep_col2, rep_col3 = st.columns([1, 8, 1])

    with rep_col1:
        sfm_gg.create_gauge_chart(0, IndicatorType.REPAIR, repair_last, "sfm_rep_gauge_last")

    with rep_col2:
        create_heatmap_chart(
            df_rep_opt, IndicatorType.REPAIR, days_rep, ref_rep, heat_label, "sfm_rep_heatmap"
        )
        create_line_chart(df_rep, IndicatorType.REPAIR)

    with rep_col3:
        sfm_gg.create_gauge_chart(1, IndicatorType.REPAIR, repair_actual, "sfm_rep_gauge")

# ============================================= Opt 2 ============================================ #
if selected_page == Sub_opt2:

    r1_col1, r1_col2, r1_col3 = st.columns([1, 1, 1])

    with r1_col1:
        with st.container(border=True):

            g1, g2, g3 = st.columns(3)
            with g1:
                sfm_gg2.create_gauge_chart(
                    IndicatorType.EFFICIENCY, efficiency_actual, "opt1_eff_gauge"
                )

            with g2:
                sfm_gg2.create_gauge_chart(
                    IndicatorType.PERFORMANCE, performance_actual, "opt1_perf_gauge"
                )

            with g3:
                sfm_gg2.create_gauge_chart(IndicatorType.REPAIR, repair_actual, "opt1_rep_gauge")

    r2_col1, r2_col2, r2_col3 = st.columns([1, 1, 1])

    with r2_col1:
        m1, m2, m3 = st.columns(3)

        with m1:
            # Filtrar pelo turno Noturno
            eff_not = round(df_eff[df_eff["turno"] == "NOT"].eficiencia.mean())
            delta_not = eff_not - efficiency_actual
            st.metric("Eficiência - Noturno", f"{eff_not} %", f"{delta_not} %")

            # Manter só o noturno e agrupar por linha
            eff_best_not = round(
                eficiencia[eficiencia["turno"] == "NOT"].groupby("linha").eficiencia.mean() * 100
            )
            # Pegar o número da linha com a maior eficiência e o valor da eficiência
            eff_best_not = eff_best_not.sort_values(ascending=False).head(1)
            eff_best_not, line_best_not = round(eff_best_not.iloc[0]), eff_best_not.index[0]
            delta_not_best_1 = round(eff_best_not - efficiency_actual)
            st.metric(f"Linha {line_best_not}", f"{eff_best_not} %", f"{delta_not_best_1} %")

            eff_worst_not = (
                eficiencia[eficiencia["turno"] == "NOT"].groupby("linha").eficiencia.mean()
            )
            eff_worst_not = eff_worst_not.sort_values(ascending=True).head(1)
            eff_worst_not, line_worst_not = round(eff_worst_not.iloc[0]), eff_worst_not.index[0]
            delta_not_worst_1 = round(eff_worst_not - efficiency_actual)
            st.metric(f"Linha {line_worst_not}", f"{eff_worst_not} %", f"{delta_not_worst_1} %")

        with m2:
            # Filtrar pelo Matutino
            eff_mat = round(df_eff[df_eff["turno"] == "MAT"].eficiencia.mean())
            delta_mat = eff_mat - efficiency_actual
            st.metric("Eficiência - Matutino", f"{eff_mat} %", f"{delta_mat} %")

            eff_best_mat = round(
                eficiencia[eficiencia["turno"] == "MAT"].groupby("linha").eficiencia.mean() * 100
            )
            eff_best_mat = eff_best_mat.sort_values(ascending=False).head(1)
            eff_best_mat, line_best_mat = round(eff_best_mat.iloc[0]), eff_best_mat.index[0]
            delta_mat_best_1 = round(eff_best_mat - efficiency_actual)
            st.metric(f"Linha {line_best_mat}", f"{eff_best_mat} %", f"{delta_mat_best_1} %")

            eff_worst_mat = (
                eficiencia[eficiencia["turno"] == "MAT"].groupby("linha").eficiencia.mean()
            )
            eff_worst_mat = eff_worst_mat.sort_values(ascending=True).head(1)
            eff_worst_mat, line_worst_mat = round(eff_worst_mat.iloc[0]), eff_worst_mat.index[0]
            delta_mat_worst_1 = round(eff_worst_mat - efficiency_actual)
            st.metric(f"Linha {line_worst_mat}", f"{eff_worst_mat} %", f"{delta_mat_worst_1} %")

        with m3:
            # Filtrar pelo Vespertino
            eff_ves = round(df_eff[df_eff["turno"] == "VES"].eficiencia.mean())
            delta_ves = eff_ves - efficiency_actual
            st.metric("Eficiência - Vespertino", f"{eff_ves} %", f"{delta_ves} %")

            eff_best_ves = round(
                eficiencia[eficiencia["turno"] == "VES"].groupby("linha").eficiencia.mean() * 100
            )
            eff_best_ves = eff_best_ves.sort_values(ascending=False).head(1)
            eff_best_ves, line_best_ves = round(eff_best_ves.iloc[0]), eff_best_ves.index[0]
            delta_ves_best_1 = round(eff_best_ves - efficiency_actual)
            st.metric(f"Linha {line_best_ves}", f"{eff_best_ves} %", f"{delta_ves_best_1} %")

            eff_worst_ves = (
                eficiencia[eficiencia["turno"] == "VES"].groupby("linha").eficiencia.mean()
            )
            eff_worst_ves = eff_worst_ves.sort_values(ascending=True).head(1)
            eff_worst_ves, line_worst_ves = round(eff_worst_ves.iloc[0]), eff_worst_ves.index[0]
            delta_ves_worst_1 = round(eff_worst_ves - efficiency_actual)
            st.metric(f"Linha {line_worst_ves}", f"{eff_worst_ves} %", f"{delta_ves_worst_1} %")

    style_metric_cards(
        background_color=ColorsSTM.LIGHT_GREY.value,
        border_left_color="white",
        border_radius_px=10,
    )

    st.write("Faltam: Principais paradas em barras")
    st.write("Fata tabela de Ocorrências")
    st.write("Falta Barras de Eficiência por linha")
