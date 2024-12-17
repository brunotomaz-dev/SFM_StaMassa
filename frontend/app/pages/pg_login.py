""" Módulo responsável por renderizar a página de login. """

import time

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.components.sfm_gauge_opt2 import create_gauge_chart
from app.functions.absent import RegistroAbsenteismo
from app.functions.get_date import GetDate
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import IndicatorType

get_date = GetDate()
this_first, this_last = get_date.get_this_month()
ind_play = IndicatorsPlayground()
reg_abs = RegistroAbsenteismo()
absent_df = reg_abs.ler_csv("Absent")
presence_df = reg_abs.ler_csv("Presence")
today, this_turn = get_date.get_this_turn()

ROLE: str = st.session_state["role"]
USER_NAME: str = st.session_state["name"]
SETORES: list[str] = [
    "Panificação",
    "Forno",
    "Pasta",
    "Recheio",
    "Embalagem",
    "Pães Diversos",
]
FALTAS_TIPOS: list[str] = [
    "Falta",
    "Atraso",
    "Afastamento",
    "Saída Antecipada",
    "Pessoas Remanejadas",
]

# ================================================================================================ #
#                                              ESTILOS                                             #
# ================================================================================================ #
# cspell: words keje6w ngngzp 10vncc0 q49buc
st.markdown(
    """
    <style>
    .st-emotion-cache-4uzi61 {
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
#                                        INICIALIZAR ESTADO                                        #
# ================================================================================================ #

if "df_reg_pres" not in st.session_state:
    st.session_state["df_reg_pres"] = pd.DataFrame(
        columns=SETORES + ["Data", "Hora", "Turno", "Usuario"]
    )
if "absenteeism" not in st.session_state:
    st.session_state["absenteeism"] = False

if "registro_presença" not in st.session_state:
    st.session_state["registro_presença"] = False


eficiencia = st.session_state.eficiencia
performance = st.session_state.performance
reparo = st.session_state.reparos
info_ihm = st.session_state.info_ihm
cart_in_greenhouse = st.session_state.cart_entering_greenhouse
production = st.session_state.produção
estoque_cam_fria = st.session_state.caixas_estoque

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
# ================================================================================================ #
SUP_TURN = None
if USER_NAME and ROLE == "supervisor":
    # cspell: words Rogerio Inacio
    SUP_TURN = {
        "Claudia Antunes": "MAT",
        "Rogerio Inacio": "VES",
        "Everton de Oliveira": "NOT",
    }[USER_NAME]


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
    if ROLE == "supervisor" and SUP_TURN:
        # Caso role = supervisor mostrar dados do turno do supervisor
        filtered_df = filtered_df[filtered_df["Turno"] == SUP_TURN]

    # Exibir os registros filtrados
    st.write("#### Registros Filtrados")
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)


# ================================================================================================ #
#                                     FORMULÁRIO DE ABSENTEÍSMO                                    #
# ================================================================================================ #


# =============================================================================== Form Absenteísmo #
@st.fragment
def att_session_state_abs():
    """
    Atualiza o estado de sessão 'absenteeism' para True ou False, dependendo do valor atual.

    Se o valor for True e o usu rio for supervisor ou dev, uma coluna com um formulário de
    absente smo  aparece na tela. O formulário tem os campos Turno, Setor, Tipo, Nome, Motivo e
    um bot o para adicionar o registro. Se o bot o for pressionado, o registro  adicionado ao
    DataFrame 'abs_df' e o estado 'absenteeism'  setado para False.

    Se o usu rio for supervisor ou dev e houver registros pendentes de envio, uma coluna com
    um DataEditor aparece na tela com os registros pendentes. O usu rio pode editar os registros
    e, se pressionar o bot o Enviar, os dados s o enviados para o arquivo CSV e o estado
    'absenteeism'  setado para False.
    """
    st.session_state["absenteeism"] = not st.session_state["absenteeism"]
    if ROLE in ["supervisor", "dev"] and st.session_state["absenteeism"]:
        form_col, d_col = st.columns([1, 2])
        with form_col:
            with st.form(key="abs", clear_on_submit=True):
                st.write("###### Dados de Absenteísmo:")
                turno = st.radio("Turno", ["Matutino", "Vespertino", "Noturno"], horizontal=True)
                s_col, t_col = st.columns([1, 1])
                setor = s_col.selectbox("Setor", [*SETORES])
                tipo = t_col.selectbox("Tipo", [*FALTAS_TIPOS])
                nome = st.text_input("Nome")
                motivo = st.text_area("Motivo")
                submit = st.form_submit_button("Adicionar")
                if submit:
                    # Atualize o estado ou faça qualquer processamento necessário
                    abs_df = reg_abs.adicionar_registro(setor, turno, nome, tipo, motivo, USER_NAME)
                    st.session_state["abs_df"] = abs_df
                    st.toast("Dados adicionados com sucesso!")
                st.session_state["absenteeism"] = False
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
                        reg_abs.salvar_csv("Absent")
                        st.toast("Dados enviados com sucesso!")
                        time.sleep(5)
                        st.session_state["absenteeism"] = False
                        st.session_state["abs_df"] = pd.DataFrame()
                        st.rerun()
                else:
                    st.write("Nenhum registro pendente.")


# ================================================================================== Form Presença #
@st.fragment
def att_session_state():
    """
    Alterna o valor de st.session_state["registro_presença"] para True/False.

    Se o valor for True, renderiza um formulário para registro de presença com campos para
    cada setor e um botão "Enviar".

    Se o formulário for submetido com sucesso, chama a função reg_abs.registrar_presenca com
    os dados do formulário e exibe uma mensagem de sucesso.

    Após o envio, volta o valor de st.session_state["registro_presença"] para False e
    recarrega a página.
    """
    st.session_state["registro_presença"] = not st.session_state["registro_presença"]
    if ROLE in ["supervisor", "dev"] and st.session_state["registro_presença"]:
        with st.container(border=True):
            with st.form(key="form_presença", border=False):
                st.write("##### Registro de Presença")
                f_col1, f_col2, f_col3, f_col4, f_col5, f_col6 = st.columns(6)
                setor_1 = f_col1.number_input("Panificação", min_value=0, max_value=100)
                setor_2 = f_col2.number_input("Forno", min_value=0, max_value=100)
                setor_3 = f_col3.number_input("Pasta", min_value=0, max_value=100)
                setor_4 = f_col4.number_input("Recheio", min_value=0, max_value=100)
                setor_5 = f_col5.number_input("Embalagem", min_value=0, max_value=100)
                setor_6 = f_col6.number_input("Pães Diversos", min_value=0, max_value=100)
                data_form = {
                    "Panificação": setor_1,
                    "Forno": setor_2,
                    "Pasta": setor_3,
                    "Recheio": setor_4,
                    "Embalagem": setor_5,
                    "Pães Diversos": setor_6,
                    "Usuario": USER_NAME,
                    "Turno": this_turn,
                }
                submit_form_pres = st.form_submit_button("Enviar")
                if submit_form_pres:
                    reg_abs.registrar_presenca(data_form)
                    time.sleep(1)
                    reg_abs.salvar_csv("Presence")
                    st.toast("Dados enviados com sucesso!")
                    time.sleep(3)
                st.session_state["registro_presença"] = False
                if submit_form_pres:
                    st.rerun()


# ================================================================================================ #
#                                              SIDEBAR                                             #
# ================================================================================================ #
if ROLE in ["supervisor", "dev"]:
    st.sidebar.divider()
    st.sidebar.write("#### Registro de Presença")
    pres = st.sidebar.button("Registrar", type="primary", use_container_width=True, key="presence")
    if pres:
        att_session_state()

    st.sidebar.write("#### Absenteísmo")
    absent = st.sidebar.button("Registrar", type="primary", use_container_width=True)
    if absent:
        att_session_state_abs()

    st.sidebar.divider()
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

# ====================================================================================== Carrinhos #
# Dataframe dos carrinhos
df_cart: pd.DataFrame = cart_in_greenhouse.copy()

# Filtrar pela data de hoje
df_cart["Data_apontamento"] = pd.to_datetime(df_cart["Data_apontamento"], format="%Y%m%d").dt.date
df_cart = df_cart[df_cart["Data_apontamento"] == today]

# Renomear colunas
df_cart.columns = ["Data", "Turno", "Carrinhos"]

# Substituir os valores de turno
df_cart["Turno"] = df_cart["Turno"].replace(
    {"MAT": "Matutino", "VES": "Vespertino", "NOT": "Noturno"}
)

# Adicionar um 'turno' Total com a soma dos carrinhos
df_cart.loc["TOTAL"] = ["", "TOTAL", df_cart["Carrinhos"].sum()]

# Ajustar a ordem do turno categorizando
df_cart["Turno"] = pd.Categorical(
    df_cart["Turno"],
    categories=["Noturno", "Matutino", "Vespertino", "TOTAL"],
    ordered=True,
)

# Remove a coluna da data
df_cart = df_cart.drop(columns=["Data"])

# Ordenar por turno
df_cart = df_cart.sort_values(by="Turno")

# Tornar o turno o índice
df_cart = df_cart.set_index("Turno")


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

# ====================================================================================== Presenças #
if presence_df.empty:
    presence_df = pd.DataFrame(columns=SETORES + ["Data", "Hora", "Turno", "Usuario"])
else:
    presence_df["Data"] = pd.to_datetime(presence_df["Data"]).dt.date
    presence_df = presence_df[presence_df["Data"] == today]

    # Supervisor / Turno
    if ROLE == "supervisor":
        # Caso role = supervisor mostrar dados do turno do supervisor
        presence_df = presence_df[presence_df["Turno"] == SUP_TURN]

    # Acrescentar uma coluna com o total de presentes somando as colunas dos setores
    presence_df["Total"] = presence_df[SETORES].sum(axis=1)
    # Agrupar por data
    presence_df = presence_df.groupby("Data").sum().drop(columns=["Hora", "Turno", "Usuario"])

    # Criar variável com total de presentes
    presentes_total = 0 if presence_df.empty else presence_df.Total.sum()

    # Criar variável com total de produção
    PRODUCTION_TOTAL = 0 if prod_total.empty else int(prod_total["Produção"].iloc[0])

# ================================================================================================ #
if absent_df.empty:
    faltas, atrasos, afastamentos, s_antecipada, remanejamento = 0, 0, 0, 0, 0
else:
    absent_df["Data"] = pd.to_datetime(absent_df["Data"]).dt.date
    absent_df = absent_df[absent_df["Data"] == today]
    faltas = absent_df[absent_df["Tipo"] == "Falta"].shape[0]
    atrasos = absent_df[absent_df["Tipo"] == "Atraso"].shape[0]
    afastamentos = absent_df[absent_df["Tipo"] == "Afastamento"].shape[0]
    s_antecipada = absent_df[absent_df["Tipo"] == "Saída Antecipada"].shape[0]
    remanejamento = absent_df[absent_df["Tipo"] == "Pessoas Remanejadas"].shape[0]

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
st.title("Dados do dia")

col_1, col_2, col_3 = st.columns([4, 2, 1])


# ========================================================================================= Gauges #
with col_1.container(border=True):
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


# =================================================================================== Presenças #
with col_3.container():
    st.subheader("Presenças")
    st.metric("Presenças", presence_df["Total"].sum())
    st.metric("Pessoas Remanejadas", remanejamento)

col_prod, col_lines, col_status = st.columns(3)

with col_prod:
    with st.container(border=True):
        # =========================================================================== Produção #
        st.subheader("Produção")

        @st.fragment(run_every=60)
        def render_table():
            """
            Fragmento que renderiza a tabela de produção na página de login.
            Este fragmento é executado a cada 60 segundos para garantir que
            os dados de produção sejam atualizados em tempo real.
            """
            st.table(df_production)

        render_table()

    with st.container(border=True):
        # ============================================================================== Carrinhos #
        st.subheader("Carrinhos Produzidos")
        st.table(df_cart)


with col_lines.container(border=True):
    # ================================================================================= Linhas #
    st.subheader("Linhas Rodando")
    if not df_info.empty:

        @st.fragment(run_every=60)
        def lines():
            """
            Fragmento que renderiza a tabela com as linhas rodando e suas respectivos produtos.
            Atualiza a cada 60 segundos.
            """
            st.table(df_info)

        lines()
    else:
        st.write("Nenhuma linha rodando.")

with col_status.container(border=True):
    # ================================================================================ Estoque #
    st.subheader("Estoque")
    st.table(estoque_cam_fria)
