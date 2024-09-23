""" Módulo responsável por renderizar a página de login. """

import asyncio

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl
from app.components.sfm_gauge_opt2 import create_gauge_chart
from app.functions.get_date import GetDate
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import IndicatorType
from app.pages.pg_sfm import get_df as get_ind

get_date = GetDate()
ind_play = IndicatorsPlayground()

# ================================================================================================ #
#                                              ESTILOS                                             #
# ================================================================================================ #

st.markdown(
    """
    <style>
    .e1f1d6gn1 .st-emotion-cache-keje6w,
    .st-emotion-cache-4uzi61 {
    padding: 10px 25px;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ================================================================================================ #
#                                         REQUISIÇÃO DE API                                        #
# ================================================================================================ #


async def get_api_data() -> pd.DataFrame:
    """Obtém os dados da API."""
    urls = [APIUrl.URL_PROD.value]
    tasks = [fetch_api_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    prod = results[0]
    return prod


@st.cache_data(ttl=60, show_spinner="Carregando dados...")
def get_data() -> pd.DataFrame:
    """Obtém os dados da API."""

    prod = asyncio.run(get_api_data())
    return prod


# ================================================================================================ #
#                                             AUTH DATA                                            #
# ================================================================================================ #
if st.session_state["authentication_status"]:
    st.header(f"Seja Bem vindo {st.session_state['name']}")

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
production = get_data()
today = get_date.get_today()


# ==================================================================================== Indicadores #
# Ajuste dos indicadores
gg_eff = ind_play.get_indicator(eficiencia, IndicatorType.EFFICIENCY, line_turn="Turno")
gg_perf = ind_play.get_indicator(performance, IndicatorType.PERFORMANCE, line_turn="Turno")
gg_rep = ind_play.get_indicator(reparo, IndicatorType.REPAIR, line_turn="Turno")

# Manter apenas os dados de hoje
gg_eff = gg_eff[pd.to_datetime(gg_eff.data_registro).dt.date == pd.to_datetime(today).date()]
gg_perf = gg_perf[pd.to_datetime(gg_perf.data_registro).dt.date == pd.to_datetime(today).date()]
gg_rep = gg_rep[pd.to_datetime(gg_rep.data_registro).dt.date == pd.to_datetime(today).date()]

# Média dos indicadores
gg_eff = gg_eff.eficiencia.mean().round(1)
gg_perf = gg_perf.performance.mean().round(1)
gg_rep = gg_rep.reparo.mean().round(1)


# ======================================================================================= Produção #
# Ajustar datas para datetime só com a data
today_day = pd.to_datetime(today).date()
production["data_registro"] = pd.to_datetime(production["data_registro"]).dt.date

# Filtrar a data de hoje
production = production[production["data_registro"] == today_day]

# Agrupar para ter a produção total por produto
production = production.groupby("produto")["total_produzido"].sum().reset_index()

# Renomear as colunas
production.columns = ["Produto", "Produção"]

# Tornar o produto o índice
production = production.set_index("Produto")

# Alterar o estilo para números no formato brasileiro


# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
st.title("Dados do dia")

col_1, col_2 = st.columns([1, 2])

with col_1:
    # ===================================================================================== Gauges #
    with st.container(border=True):
        st.subheader("Indicadores")
        g1, g2, g3 = st.columns(3)
        with g1:
            create_gauge_chart(IndicatorType.EFFICIENCY, gg_eff, "login_eff_gauge", pos="top")
        with g2:
            create_gauge_chart(IndicatorType.PERFORMANCE, gg_perf, "login_perf_gauge")
        with g3:
            create_gauge_chart(IndicatorType.REPAIR, gg_rep, "login_rep_gauge", pos="top")

    # ================================================================================ Absenteísmo #
    with st.container(border=True):
        st.subheader("Absenteísmo")
        st.write("Em desenvolvimento")

with col_2:
    col_2_1, col_2_2 = st.columns(2)
    with col_2_1:
        # =============================================================================== Produção #
        with st.container():
            st.subheader("Produção")
            st.table(production)
    with col_2_2:
        # ================================================================================= Linhas #
        with st.container():
            st.subheader("Linhas Rodando")
            st.write("Em desenvolvimento")

    with st.container(border=True):
        # ================================================================================ Estoque #
        st.subheader("Estoque")
        st.write("Em desenvolvimento")
