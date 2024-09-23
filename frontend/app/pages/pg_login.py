""" Módulo responsável por renderizar a página de login. """

import streamlit as st

# pylint: disable=import-error
from app.components.sfm_gauge_opt2 import create_gauge_chart
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import IndicatorType
from app.pages.pg_sfm import get_df as get_ind

ind_play = IndicatorsPlayground()


# ================================================================================================ #
#                                             AUTH DATA                                            #
# ================================================================================================ #
if st.session_state["authentication_status"]:
    st.title(f"Seja Bem vindo {st.session_state['name']}")

    if st.session_state["role"] == "dev":
        st.subheader("Desenvolvedor")
        st.sidebar.write("Opções:")
        add_user = st.sidebar.button("Adicionar Usuário")

        if add_user:
            st.session_state["add_user"] = 1 if st.session_state["add_user"] == 0 else 0
            st.rerun()

    pass_reset = st.sidebar.button("Alterar Senha")
    if pass_reset:
        st.session_state["pass_reset"] = 1 if st.session_state["pass_reset"] == 0 else 0
        st.rerun()

# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #

eficiencia, performance, reparo, _, _ = get_ind()

# Ajuste dos indicadores
gg_eff = ind_play.get_indicator(eficiencia, IndicatorType.EFFICIENCY, line_turn="Turno")
gg_perf = ind_play.get_indicator(performance, IndicatorType.PERFORMANCE, line_turn="Turno")
gg_rep = ind_play.get_indicator(reparo, IndicatorType.REPAIR, line_turn="Turno")

gg_eff = gg_eff.eficiencia.mean().round(2)
gg_perf = gg_perf.performance.mean().round(2)
gg_rep = gg_rep.reparo.mean().round(2)

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
col_1, col_2 = st.columns([1, 2])

with col_1:
    # ===================================================================================== Gauges #
    with st.container():
        g1, g2, g3 = st.columns(3)
        with g1:
            create_gauge_chart(IndicatorType.EFFICIENCY, gg_eff, "login_eff_gauge")
        with g2:
            create_gauge_chart(IndicatorType.PERFORMANCE, gg_perf, "login_perf_gauge")
        with g3:
            create_gauge_chart(IndicatorType.REPAIR, gg_rep, "login_rep_gauge")

    # ================================================================================ Absenteísmo #
    with st.container(border=True):
        st.title("Absenteísmo")

with col_2:
    col_2_1, col_2_2 = st.columns(2)
    with col_2_1:
        # =============================================================================== Produção #
        with st.container(border=True):
            st.title("Produção")
    with col_2_2:
        # ================================================================================= Linhas #
        with st.container(border=True):
            st.title("Linhas Rodando")

    with st.container(border=True):
        # ================================================================================ Estoque #
        st.title("Estoque")
