"""Módulo que contém a página de visualização de todas as linhas de um histograma."""

import asyncio

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl
from app.components.sfm_gauge_opt2 import create_gauge_chart
from app.functions.get_date import GetDate
from app.helpers.timer_decorator import timer_decorator
from app.helpers.variables import COLOR_DICT, IndicatorType

get_date = GetDate()

FIRST_DAY, LAST_DAY = get_date.get_this_month()
TODAY = get_date.get_today()
TURN_DICT = None
LINE_PICKED = None

# ================================================================================================ #
#                                               STYLE                                              #
# ================================================================================================ #

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
#                                    REQUISIÇÃO DE DADOS DA API                                    #
# ================================================================================================ #


async def get_data(selected_date: pd.Timestamp) -> pd.DataFrame:
    """Função para buscar os dados da API."""

    url = f"{APIUrl.URL_MAQ_INFO.value}?start={selected_date}&end={selected_date}"

    data = await fetch_api_data(url)

    return data


@timer_decorator
@st.cache_data(max_entries=1, show_spinner="Lendo dados...")
def get_api_data(chosen_date: pd.Timestamp) -> None:
    """
    Função para buscar os dados da API a cada 60 segundos e
    atualizar a variável de estado 'maquina_info' com os dados
    obtidos. Isso garante que os dados sejam atualizados mesmo
    quando o usuário não interage com a aplicação.
    """

    maquina_info_data = asyncio.run(get_data(chosen_date))
    if maquina_info_data.empty:
        st.error("Não foi possível carregar os dados.")
        st.stop()
    else:
        st.session_state["maquina_info"] = maquina_info_data


# Encontrar a data de ontem baseado em TODAY
yesterday = TODAY - pd.Timedelta(days=1)

if "maquina_info" not in st.session_state:
    get_api_data(yesterday)


# ================================================================================================ #
#                                              SIDEBAR                                             #
# ================================================================================================ #

st.sidebar.title("Configurações")

date_picked = st.sidebar.date_input(
    "Escolha a data",
    value=yesterday,
    min_value=TODAY - pd.DateOffset(days=31),
    max_value=yesterday,
    format="DD/MM/YYYY",
)

if date_picked:
    get_api_data(date_picked)
    LINE_PICKED = st.sidebar.selectbox("Escolha a linha", list(range(1, 15)))

    turn_picked = st.sidebar.selectbox(
        "Escolha o turno", ["Todos", "Matutino", "Vespertino", "Noturno"]
    )

    if turn_picked != "Todos":
        TURN_DICT = {"Matutino": "MAT", "Vespertino": "VES", "Noturno": "NOT"}[turn_picked]

# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #

maq_info = st.session_state.maquina_info
eficiencia = st.session_state.eficiencia
performance = st.session_state.performance
reparos = st.session_state.reparos
info_ihm = st.session_state.info_ihm
production = st.session_state.produção

# Ajustar a data para datetime
info_ihm.data_registro = pd.to_datetime(info_ihm.data_registro).dt.date
eficiencia.data_registro = pd.to_datetime(eficiencia.data_registro).dt.date
performance.data_registro = pd.to_datetime(performance.data_registro).dt.date
reparos.data_registro = pd.to_datetime(reparos.data_registro).dt.date
maq_info.data_registro = pd.to_datetime(maq_info.data_registro).dt.date
production.data_registro = pd.to_datetime(production.data_registro).dt.date

# Filtra pela data escolhida
if date_picked:
    info_ihm = info_ihm[info_ihm.data_registro == date_picked]
    eficiencia = eficiencia[eficiencia.data_registro == date_picked]
    performance = performance[performance.data_registro == date_picked]
    reparos = reparos[reparos.data_registro == date_picked]
    maq_info = maq_info[maq_info.data_registro == date_picked]
    production = production[production.data_registro == date_picked]

# ========================================================================================= Barras #
bar_df = info_ihm.copy()

# Se o status for rodando o motivo também deve ser rodando
bar_df.motivo = np.where(bar_df.status == "rodando", "Rodando", bar_df.motivo)

# Se o motivo estiver vazio preenche com "Não Apontado"
bar_df.motivo = bar_df["motivo"].fillna("Não apontado")

# Ajustar as datas para pd.Datetime
bar_df.data_registro = pd.to_datetime(bar_df.data_registro).dt.date
bar_df.data_registro_ihm = pd.to_datetime(bar_df.data_registro_ihm).dt.date

# Ajustar a hora
bar_df.hora_registro = pd.to_datetime(bar_df.hora_registro, format="%H:%M:%S.%f").dt.time
bar_df.hora_registro_ihm = pd.to_datetime(bar_df.hora_registro_ihm, format="%H:%M:%S.%f").dt.time

# Se o motivo for parada programada e a causa for Refeição, ajustar o motivo para Refeição
bar_df.motivo = np.where(
    (bar_df.motivo == "Parada Programada") & (bar_df.causa == "Refeição"), "Refeição", bar_df.motivo
)

# Agrupar pela linha, data, motivo, somando o tempo e mantendo a hora de registro
bar_df = (
    bar_df.groupby(["linha", "data_registro", "turno", "motivo"])
    .agg(
        {
            "tempo": "sum",
            "hora_registro": "first",
        }
    )
    .reset_index()
)

bar_df = bar_df.sort_values(by=["linha", "motivo"]).reset_index(drop=True)

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

# Verificar se nenhum dataframe está vazio para exibir o gráfico
if not date_picked:
    st.stop()

# cSpell: words pareto
# Faz cópia dos dataframes a serem utilizados
eficiencia_df = eficiencia.copy()
performance_df = performance.copy()
reparos_df = reparos.copy()
pareto_df = bar_df.copy()

# Filtra pela linha escolhida e pelo turno escolhido
eficiencia_df = eficiencia_df[eficiencia_df.linha == LINE_PICKED]
performance_df = performance_df[performance_df.linha == LINE_PICKED]
reparos_df = reparos_df[reparos_df.linha == LINE_PICKED]
pareto_df = pareto_df[pareto_df.linha == LINE_PICKED]
maq_info = maq_info[maq_info.linha == LINE_PICKED]
production = production[production.linha == LINE_PICKED]

if TURN_DICT:
    eficiencia_df = eficiencia_df[eficiencia_df.turno == TURN_DICT]
    performance_df = performance_df[performance_df.turno == TURN_DICT]
    reparos_df = reparos_df[reparos_df.turno == TURN_DICT]
    pareto_df = pareto_df[pareto_df.turno == TURN_DICT]
    maq_info = maq_info[maq_info.turno == TURN_DICT]
    production = production[production.turno == TURN_DICT]

if eficiencia_df.empty:
    st.write("Sem dados para a data escolhida.")
    st.stop()


col_1, col_2 = st.columns([1, 2], vertical_alignment="center")
# ===================================================================================== Gauges #
with col_1.container():
    col_eff, col_perf, col_rep = st.columns(3)
    # Pegar a eficiência, performance e reparos
    eficiencia_df = (eficiencia_df.eficiencia.fillna(0).mean() * 100).round(1)
    performance_df = (performance_df.performance.fillna(0).mean() * 100).round(1)
    reparos_df = (reparos_df.reparo.fillna(0).mean() * 100).round(1)

    with col_eff.container():
        create_gauge_chart(IndicatorType.EFFICIENCY, eficiencia_df, "all-hist-eff")
    with col_perf.container():
        create_gauge_chart(IndicatorType.PERFORMANCE, performance_df, "all-hist-perf")
    with col_rep.container():
        create_gauge_chart(IndicatorType.REPAIR, reparos_df, "all-hist-rep")

# ============================================================================== Pareto E Produção #
with col_2.container():
    prod_col, pareto_col = st.columns([1, 3], vertical_alignment="center")
    # =================================================================================== Produção #
    with prod_col.container():
        # Soma da Produção
        production_sum = production.total_produzido.sum()
        # Garantir que a soma não seja nula
        production_sum = production_sum if not pd.isna(production_sum) else 0
        # Garantir que a soma não seja negativa
        production_sum = production_sum.clip(min=0)
        # Formatar o número para o formato brasileiro
        production_sum = f"{production_sum:,.0f}".replace(",", ".")

        # Lista dos produtos únicos
        products = production.produto.unique()

        st.markdown(
            f"""
            <div class="card_production">
            <p style="font-size: 0.7vw; text-align: left; padding-left: 0.5vw;
            margin-bottom: 0; margin-top: 10px;">Produção</p>
            <h1 style="font-size: 1.1vw;">{'<br>'.join(products)}</h1>
             <p style="font-size: 0.7vw; text-align: left ;
            padding-left: 0.5vw ; margin-bottom: 0;">Produção de Bandejas</p>
            <h1 style="font-size: 2vw;">{production_sum}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ===================================================================================== Pareto #
    with pareto_col.container():

        # Remove os motivos rodando e parada programada
        pareto_df = pareto_df[~pareto_df.motivo.isin(["Rodando", "Parada Programada", "Refeição"])]

        # Agrupar por motivo e somar o tempo
        pareto_df = (
            pareto_df.groupby("motivo", observed=False)
            .agg({"tempo": "sum"})
            .reset_index()
            .sort_values(by="tempo", ascending=False)
        )

        # Calcular o percentual
        pareto_df["percentual"] = (pareto_df.tempo / pareto_df.tempo.sum() * 100).round(2)

        # Ordenar pelo percentual
        pareto_df = pareto_df.sort_values(by="percentual", ascending=False)

        # Plot
        pareto_fig = (
            alt.Chart(pareto_df)
            .mark_bar(orient="horizontal", color="darkgray")
            .encode(
                y=alt.Y("motivo:N", title="Motivo", sort="-x", axis=alt.Axis()),
                x=alt.X("percentual:Q", title="Percentual entre paradas (%)"),
                tooltip=[
                    alt.Tooltip("motivo:N", title="Motivo"),
                    alt.Tooltip("tempo:Q", title="Tempo (min)"),
                    alt.Tooltip("percentual:Q", title="Percentual (%)"),
                ],
            )
        )

        st.altair_chart(pareto_fig, use_container_width=True)

# =========================================================================== Linhas De Ciclos #
with st.container():
    # Ajustar a hora
    maq_info.hora_registro = pd.to_datetime(maq_info.hora_registro, format="%H:%M:%S")

    # Manter apenas o status rodando
    maq_info_stops = maq_info[maq_info.status == "rodando"]

    # Média dos ciclos
    media_ciclos = maq_info_stops.ciclo_1_min.mean().round(2) if len(maq_info_stops) > 0 else 0

    # Figura principal com ciclos
    fig_ciclos = (
        alt.Chart(maq_info)
        .mark_line(color="darkgray")
        .encode(
            x=alt.X("hora_registro:T", title="Hora", axis=alt.Axis(format="%H:%M")),
            y=alt.Y("ciclo_1_min:Q", title="Ciclos"),
            tooltip=[
                alt.Tooltip("hora_registro:T", title="Hora", format="%H:%M"),
                alt.Tooltip("ciclo_1_min:Q", title="Ciclos"),
            ],
        )
    )

    # Figura com a linha média
    fig_media = (
        alt.Chart(pd.DataFrame({"ciclos_media": [media_ciclos]}))
        .mark_rule(color="cadetblue")
        .encode(y="ciclos_media:Q", tooltip=[alt.Tooltip("ciclos_media:Q", title="Média")])
        .properties(title=f"Média de Ciclos: {media_ciclos:.2f}")
    )

    # Texto da média
    fig_text = (
        alt.Chart(pd.DataFrame({"ciclos_media": [media_ciclos]}))
        .mark_text(color="cadetblue", dy=-10, fontSize=12)
        .encode(
            y=alt.Y("ciclos_media:Q"),
            text=alt.Text("ciclos_media:Q", format=".2f"),
            tooltip=[alt.Tooltip("ciclos_media:Q", title="Média")],
        )
    )

    # Figura final
    fig_ciclos = alt.layer(fig_ciclos, fig_media, fig_text).properties(height=200)

    st.altair_chart(fig_ciclos, use_container_width=True)
# =================================================================================== Timeline #
with st.container():
    # Fazer uma cópia do dataframe
    timeline_df = info_ihm.copy()

    # Filtrar pela linha
    timeline_df = timeline_df[timeline_df.linha == LINE_PICKED]

    # Filtrar pelo turno
    if TURN_DICT:
        timeline_df = timeline_df[timeline_df.turno == TURN_DICT]

    # Onde o status é rodando, mudar o motivo para Rodando
    timeline_df.motivo = np.where(timeline_df.status == "rodando", "Rodando", timeline_df.motivo)

    # Onde o motivo for vazio, preencher com Não Apontado
    timeline_df.motivo = timeline_df["motivo"].fillna("Não apontado")
    timeline_df.causa = timeline_df.causa.fillna("")

    # Se a causa for refeição, mudar o motivo para Refeição
    timeline_df.motivo = np.where(
        (timeline_df.motivo != "Saída para Backup") & (timeline_df.causa == "Refeição"),
        "Refeição",
        timeline_df.motivo,
    )

    # Ajustar a cor
    color_timeline = {motivo: COLOR_DICT[motivo] for motivo in timeline_df["motivo"].unique()}

    # Figura
    timeline_fig = (
        alt.Chart(timeline_df)
        .mark_bar(size=20)
        .encode(
            x=alt.X("data_hora:T", title="Hora", axis=alt.Axis(format="%H:%M")),
            x2="data_hora_final:T",
            y=alt.Y("data_registro", title="Timeline", axis=alt.Axis(labels=False)),
            color=alt.Color(
                "motivo:N",
                scale=alt.Scale(
                    domain=list(color_timeline.keys()), range=list(color_timeline.values())
                ),
                legend=alt.Legend(orient="top"),
                title="Motivo",
            ),
            tooltip=[
                alt.Tooltip("motivo:N", title="Motivo"),
                alt.Tooltip("causa:N", title="Causa"),
                alt.Tooltip("data_hora:T", title="Hora Inicial", format="%H:%M"),
                alt.Tooltip("data_hora_final:T", title="Hora Final", format="%H:%M"),
                alt.Tooltip("tempo", title="Tempo (minutos)"),
            ],
        )
        .properties(height=200)
    )

    st.altair_chart(timeline_fig, use_container_width=True)

# ========================================================================================= Tabela #
with st.expander("Tabelas dos indicadores"):
    # Aplicar os filtros
    eficiencia = eficiencia[eficiencia.linha == LINE_PICKED]
    performance = performance[performance.linha == LINE_PICKED]
    reparos = reparos[reparos.linha == LINE_PICKED]

    # Ajustar as tabelas
    eficiencia.eficiencia = eficiencia.eficiencia * 100
    performance.performance = performance.performance * 100
    reparos.reparo = reparos.reparo * 100
    eficiencia.hora_registro = pd.to_datetime(
        eficiencia.hora_registro, format="%H:%M:%S.%f"
    ).dt.time
    performance.hora_registro = pd.to_datetime(
        performance.hora_registro, format="%H:%M:%S.%f"
    ).dt.time
    reparos.hora_registro = pd.to_datetime(reparos.hora_registro, format="%H:%M:%S.%f").dt.time
    eficiencia.data_registro = pd.to_datetime(eficiencia.data_registro).dt.date
    performance.data_registro = pd.to_datetime(performance.data_registro).dt.date
    reparos.data_registro = pd.to_datetime(reparos.data_registro).dt.date

    # Ordenar os turnos na order: NOT, MAT, VES
    eficiencia.turno = pd.Categorical(
        eficiencia.turno, categories=["NOT", "MAT", "VES"], ordered=True
    )
    performance.turno = pd.Categorical(
        performance.turno, categories=["NOT", "MAT", "VES"], ordered=True
    )
    reparos.turno = pd.Categorical(reparos.turno, categories=["NOT", "MAT", "VES"], ordered=True)
    eficiencia = eficiencia.sort_values(by="turno")
    performance = performance.sort_values(by="turno")
    reparos = reparos.sort_values(by="turno")

    eficiencia = eficiencia.style.format(thousands=".", decimal=",", precision=1)
    performance = performance.style.format(thousands=".", decimal=",", precision=1)
    reparos = reparos.style.format(thousands=".", decimal=",", precision=1)

    st.dataframe(eficiencia, use_container_width=True, hide_index=True)
    st.dataframe(performance, use_container_width=True, hide_index=True)
    st.dataframe(reparos, use_container_width=True, hide_index=True)
