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

ROLE = st.session_state["role"]

# ================================================================================================ #
#                                              ESTILOS                                             #
# ================================================================================================ #
# cspell: words keje6w
st.markdown(
    """
    <style>
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


async def get_api_data() -> tuple:
    """Obtém os dados da API."""
    urls = [APIUrl.URL_PROD.value, APIUrl.URL_CAIXAS_ESTOQUE.value]
    tasks = [fetch_api_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    production_result, caixas_cf = results

    return production_result, caixas_cf


@st.cache_data(ttl=60, show_spinner="Carregando dados...")
def get_data() -> tuple:
    """Obtém os dados da API."""

    production_result, caixas_cf = asyncio.run(get_api_data())
    return production_result, caixas_cf


# ================================================================================================ #
#                                             AUTH DATA                                            #
# ================================================================================================ #
if st.session_state["authentication_status"]:
    st.header(f"Olá {st.session_state['name']}")
    st.write(f'##### Login de _{st.session_state["role"].capitalize()}_')

    pass_reset = st.sidebar.button("Alterar Senha")

    if pass_reset:
        st.session_state["pass_reset"] = 1 if st.session_state["pass_reset"] == 0 else 0
        st.rerun()

if ROLE == "dev":
    st.sidebar.write("Opções:")
    add_user = st.sidebar.button("Adicionar Usuário")

    if add_user:
        st.session_state["add_user"] = 1 if st.session_state["add_user"] == 0 else 0
        st.rerun()


if ROLE == "supervisor":
    st.sidebar.divider()

# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #

eficiencia, performance, reparo, _, info_ihm = get_ind()
production, estoque_cam_fria = get_data()
today, this_turn = get_date.get_this_turn()


# ==================================================================================== Indicadores #
# Ajuste dos indicadores
gg_eff = ind_play.get_indicator(eficiencia, IndicatorType.EFFICIENCY, line_turn="Turno")
gg_perf = ind_play.get_indicator(performance, IndicatorType.PERFORMANCE, line_turn="Turno")
gg_rep = ind_play.get_indicator(reparo, IndicatorType.REPAIR, line_turn="Turno")

# Manter apenas os dados de hoje
gg_eff = gg_eff[pd.to_datetime(gg_eff.data_registro).dt.date == today]
gg_perf = gg_perf[pd.to_datetime(gg_perf.data_registro).dt.date == today]
gg_rep = gg_rep[pd.to_datetime(gg_rep.data_registro).dt.date == today]

# Média dos indicadores
gg_eff = gg_eff.eficiencia.mean().round(1)
gg_perf = gg_perf.performance.mean().round(1)
gg_rep = gg_rep.reparo.mean().round(1)

# ======================================================================================= Produção #
# Ajustar datas para datetime só com a data
production["data_registro"] = pd.to_datetime(production["data_registro"]).dt.date

# Filtrar a data de hoje
production = production[production["data_registro"] == today]

# Agrupar para ter a produção total por produto
df_production = production.groupby("produto")["total_produzido"].sum().reset_index()

# Renomear as colunas
df_production.columns = ["Produto", "Produção"]

# Ajustar a produção para caixas (dividir por 10)
df_production["Produção"] = df_production["Produção"] / 10

# Tornar o produto o índice
df_production = df_production.set_index("Produto")

prod_total = df_production.sum(axis=0).to_frame().T
prod_total.index = ["TOTAL"]
df_production = pd.concat([df_production, prod_total])

# Alterar o estilo para números no formato brasileiro
df_production = df_production.style.format(thousands=".", decimal=",", precision=0)

# ================================================================================= Linhas Rodando #
# Ajustar data e filtrar
info_ihm.data_registro = pd.to_datetime(info_ihm.data_registro).dt.date
df_info = info_ihm[info_ihm.data_registro == today]
# Filtrar pelo turno
df_info = df_info[df_info.turno == this_turn]
# Manter apenas o último registro de cada linha/máquina
df_info = df_info.sort_values(by=["linha", "maquina_id", "data_hora"])
df_info = df_info.groupby(["linha", "maquina_id"]).tail(1).reset_index(drop=True)
# Manter apenas as linhas com status rodando
df_info = df_info[df_info.status == "rodando"]
# Manter apenas a coluna de linha
df_info = df_info[["linha"]]

# Pegar a produção
prod = production[production.turno == this_turn]
# Manter a linha e o produto
prod = prod[["linha", "produto"]]

# Alterar o nome da coluna
prod = prod.rename(columns={"produto": "Produto"})

# Juntar com as informações das linhas
df_info = df_info.merge(prod, how="left", left_on="linha", right_on="linha")

# Ajustar os valores da coluna linha para melhor visualização, incluindo "Linha: "
df_info["linha"] = "Linha: " + df_info["linha"].astype(str)

# Fazer da linha o index
df_info = df_info.set_index("linha")

# ======================================================================================== Estoque #

# Tornar a coluna produto o index
estoque_cam_fria = estoque_cam_fria.set_index("produto")
# Ordenar pela quantidade
estoque_cam_fria = estoque_cam_fria.sort_values(by="quantidade", ascending=False)
# Remover onde a quantidade é zero
estoque_cam_fria = estoque_cam_fria[estoque_cam_fria["quantidade"] > 0]
# Capitalizar coluna
estoque_cam_fria.columns = estoque_cam_fria.columns.str.capitalize()
# Adicionar o total
estoque_cam_fria.loc["TOTAL"] = estoque_cam_fria.sum()

# Ajustar os valores para formato brasileiro
estoque_cam_fria = estoque_cam_fria.style.format(thousands=".", decimal=",", precision=0)


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
        with st.container(border=True):
            st.subheader("Produção")
            st.table(df_production)
        # ================================================================================= Linhas #
        with st.container(border=True):
            st.subheader("Linhas Rodando")
            st.table(df_info)
    with col_2_2:
        # ================================================================================ Estoque #
        with st.container(border=True):
            st.subheader("Estoque")
            st.table(estoque_cam_fria)
