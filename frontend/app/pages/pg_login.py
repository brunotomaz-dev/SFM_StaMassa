""" Módulo responsável por renderizar a página de login. """

import asyncio

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl
from app.components.sfm_gauge_opt2 import create_gauge_chart
from app.functions.asbsent import RegistroAbsenteismo
from app.functions.get_date import GetDate
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import IndicatorType

get_date = GetDate()
this_first, this_last = get_date.get_this_month()
ind_play = IndicatorsPlayground()
reg_abs = RegistroAbsenteismo()
absent_df = reg_abs.ler_csv()

ROLE = st.session_state["role"]
USER_NAME = st.session_state["name"]
SETORES = ["Panificação", "Recheio", "Embalagem", "Pasta", "Forno", "Pães Diversos"]
FALTAS_TIPOS = ["Falta", "Atraso", "Afastamento", "Saída Antecipada"]

# ================================================================================================ #
#                                              ESTILOS                                             #
# ================================================================================================ #
# cspell: words keje6w
st.markdown(
    """
    <style>
    .st-emotion-cache-4uzi61,
    .st-emotion-cache-fplge5,
    .st-emotion-cache-1yycg8b {
    padding: 10px 25px;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricValue"] {
    font-size: 4vw;
    text-align: center;
    }
    .st-emotion-cache-q49buc {
        color: #000;
    }
    [data-testid="stMetric"] {
        background-color: #fff;
        color: #000;
        padding: 5px 15px;
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


async def retrieve_data() -> tuple:
    """
    Obtém os dados da API.

    Returns:
        tuple: Tupla contendo os DataFrames de eficiência, performance, reparo e informações da IHM.
    """
    urls = [
        APIUrl.URL_EFF.value,
        APIUrl.URL_PERF.value,
        APIUrl.URL_REP.value,
        APIUrl.URL_INFO_IHM.value,
    ]
    tasks = [fetch_api_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    ef, pe, re, ii = results

    return ef, pe, re, ii


@st.cache_data(ttl=60, show_spinner="Carregando dados...")
def get_data() -> tuple:
    """Obtém os dados da API."""

    production_result, caixas_cf = asyncio.run(get_api_data())
    return production_result, caixas_cf


@st.cache_data(ttl=60 * 10, show_spinner="Carregando dados...")
def get_ind() -> tuple:
    """Obtém os dados da API.
    Retorna:
    Eficiência, performance, reparo e informações da IHM.
    """
    eff, perf, rep, inf_ihm = asyncio.run(retrieve_data())
    return eff, perf, rep, inf_ihm


# ================================================================================================ #
#                                             AUTH DATA                                            #
# ================================================================================================ #
if st.session_state["authentication_status"]:
    role = st.session_state["role"].replace("-", " ").title()
    st.header(f"Olá {st.session_state['name']}")
    st.write(f"##### Login de _{role}_")

    pass_reset = st.sidebar.button("Alterar Senha")

    if pass_reset:
        st.session_state["pass_reset"] = 1 if st.session_state["pass_reset"] == 0 else 0
        st.rerun()


# ================================================================================================ #
#                                               MODAL                                              #
# ================================================================================================


@st.dialog("Registros de Absenteísmo", width="large")
def show_absent(
    df: pd.DataFrame,
    abs_date: list,
    abs_name: str | None = None,
    abs_setor: str = "",
    abs_type: str = "",
):
    """Mostra os registros de absenteísmo."""

    df["Data"] = pd.to_datetime(df["Data"]).dt.date

    # Construir a string de consulta usando as variáveis
    query_str = "Data >= @abs_date[0] and Data <= @abs_date[1]"
    if abs_name:
        query_str += " and Nome.str.contains(@abs_name, case=False)"
    if abs_setor:
        query_str += " and Setor == @abs_setor"
    if abs_type:
        query_str += " and Tipo == @abs_type"

    # Filtrar o DataFrame usando query
    filtered_df = df.query(
        query_str,
        local_dict={
            "abs_date": abs_date,
            "abs_name": abs_name,
            "abs_setor": abs_setor,
            "abs_type": abs_type,
        },
    )

    # Supervisor / Turno
    if ROLE == "supervisor":
        sup_turn = {
            "Claudia Antunes": "MAT",
            "Rogerio Inacio": "VES",
            "Everton de Oliveira": "NOT",
        }[USER_NAME]

        # Caso role = supervisor mostrar dados do turno do supervisor
        filtered_df = filtered_df[filtered_df["Turno"] == sup_turn]

    # Exibir os registros filtrados
    st.write("#### Registros Filtrados")
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)


# ================================================================================================ #
#                                              SIDEBAR                                             #
# ================================================================================================ #
if "absenteeism" not in st.session_state:
    st.session_state["absenteeism"] = False
if ROLE in ["supervisor", "dev"]:
    st.sidebar.divider()
    st.sidebar.write("#### Absenteísmo")
    absent = st.sidebar.button("Registrar", type="primary", use_container_width=True)
    if absent:
        st.session_state["absenteeism"] = not st.session_state["absenteeism"]
        st.rerun()

    with st.sidebar.form(key="absenteeism-form-search", clear_on_submit=True):

        st.write("##### Consultar Registros")
        absent_date = st.date_input(
            "Data",
            max_value=get_date.get_today(),
            min_value=pd.to_datetime(this_first).date(),
            format="DD/MM/YYYY",
            value=[get_date.get_today(), get_date.get_today()],
        )
        absent_name = st.text_input("Nome")
        absent_setor = st.selectbox("Setor", ["", *SETORES])
        absent_type = st.selectbox("Tipo", ["", *FALTAS_TIPOS])
        submit_form = st.form_submit_button("Buscar")
    if submit_form:
        show_absent(absent_df, absent_date, absent_name, absent_setor, absent_type)

if ROLE == "dev":
    st.sidebar.divider()
    st.sidebar.write("Opções de Desenvolvedor:")
    add_user = st.sidebar.button("Adicionar Usuário")

    if add_user:
        st.session_state["add_user"] = 1 if st.session_state["add_user"] == 0 else 0
        st.rerun()

# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #

eficiencia, performance, reparo, info_ihm = get_ind()
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

if gg_eff["eficiencia"].isnull().all():
    gg_eff["eficiencia"] = gg_eff["eficiencia"].fillna(0)
    gg_perf["performance"] = gg_perf["performance"].fillna(0)
    gg_rep["reparo"] = gg_rep["reparo"].fillna(0)

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
#                                     FORMULÁRIO DE ABSENTEÍSMO                                    #
# ================================================================================================ #

# =============================================================================== Form Absenteísmo #
if ROLE in ["supervisor", "dev"] and st.session_state["absenteeism"]:
    f_col, d_col = st.columns([1, 2])
    with f_col:
        with st.form(key="abs", clear_on_submit=True):
            st.write("###### Dados de Absenteísmo:")
            turno = st.radio("Turno", ["Matutino", "Vespertino", "Noturno"], horizontal=True)
            s_col, t_col = st.columns([1, 1])
            setor = s_col.selectbox("Setor", [*SETORES])
            tipo = t_col.selectbox("Tipo", [*FALTAS_TIPOS])
            nome = st.text_input("Nome")
            motivo = st.text_area("Motivo")
            col_sub, col_save = st.columns([4, 1])
            submit = col_sub.form_submit_button("Adicionar")
            if submit:
                # Atualize o estado ou faça qualquer processamento necessário
                abs_df = reg_abs.adicionar_registro(setor, turno, nome, tipo, motivo, USER_NAME)
                st.session_state["abs_df"] = abs_df
                st.toast("Dados adicionados com sucesso!")
    with d_col:
        with st.container(border=True):
            st.write("###### Registros de Absenteísmo pendentes de envio:")
            if "abs_df" in st.session_state and not st.session_state["abs_df"].empty:
                abs_df_edited = st.data_editor(
                    st.session_state["abs_df"],
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                )
                enviar = st.button("Enviar")
                if enviar:
                    # cspell: word absenteismo
                    st.session_state["absenteismo_df"] = abs_df_edited
                    reg_abs.salvar_csv()
                    st.toast("Dados enviados com sucesso!")
                    st.session_state["absenteeism"] = False
                    st.session_state["abs_df"] = pd.DataFrame()
                    st.rerun()
            else:
                st.write("Nenhum registro pendente.")

# ================================================================================================ #
if absent_df.empty:
    faltas, atrasos, afastamentos, s_antecipada = 0, 0, 0, 0
else:
    absent_df["Data"] = pd.to_datetime(absent_df["Data"]).dt.date
    absent_df = absent_df[absent_df["Data"] == today]
    faltas = absent_df[absent_df["Tipo"] == "Falta"].shape[0]
    atrasos = absent_df[absent_df["Tipo"] == "Atraso"].shape[0]
    afastamentos = absent_df[absent_df["Tipo"] == "Afastamento"].shape[0]
    s_antecipada = absent_df[absent_df["Tipo"] == "Saída Antecipada"].shape[0]

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
st.title("Dados do dia")

col_1, col_2 = st.columns([1.5, 1])

# ========================================================================================= Gauges #
with col_1.container():
    st.subheader("Indicadores")
    g1, g2, g3 = st.columns(3, gap="large", vertical_alignment="center")
    with g1:
        create_gauge_chart(IndicatorType.EFFICIENCY, gg_eff, "login_eff_gauge", large=True)
    with g2:
        create_gauge_chart(IndicatorType.PERFORMANCE, gg_perf, "login_perf_gauge", large=True)
    with g3:
        create_gauge_chart(IndicatorType.REPAIR, gg_rep, "login_rep_gauge", large=True)

# ==================================================================================== Absenteísmo #
with col_2.container():
    st.subheader("Absenteísmo")
    f_col, a_col = st.columns(2)
    f_col.metric("Faltas", faltas)
    a_col.metric("Atrasos", atrasos)
    af_col, sa_col = st.columns(2)
    af_col.metric("Afastamentos", afastamentos)
    sa_col.metric("Saídas Antecipadas", s_antecipada)

col_prod, col_lines, col_status = st.columns(3)

with col_prod.container(border=True):
    # =============================================================================== Produção #
    st.subheader("Produção")
    st.table(df_production)

with col_lines.container(border=True):
    # ================================================================================= Linhas #
    st.subheader("Linhas Rodando")
    if not df_info.empty:
        st.table(df_info)
    else:
        st.write("Nenhuma linha rodando.")

with col_status.container(border=True):
    # ================================================================================ Estoque #
    st.subheader("Estoque")
    st.table(estoque_cam_fria)
