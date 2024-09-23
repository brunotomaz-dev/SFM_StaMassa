"""Página de visão das linhas."""

import asyncio
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

# pylint: disable=E0401
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl
from app.components.sfm_gauge_opt2 import create_gauge_chart
from app.functions.get_date import GetDate
from app.helpers.variables import COLOR_DICT, ColorsSTM, IndicatorType

get_date = GetDate()

# Receber a data e turno atual
today, turn = get_date.get_this_turn()
# Receber a hora
now = get_date.get_today()

#    ┏━                                                                                    ━┓
#    ┃                                       Estilos                                        ┃
#    ┗━                                                                                    ━┛
st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 4vw;
    text-align: center;
}
[data-testid="stMetric"] {
    background-color: #fff;
    padding: 10px 25px;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
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
.card3 {
    text-align: center;
    font-size: 1vw;"""
    + ColorsSTM.LIGHT_GREY.value
    + """
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    height: 100%;
}
.sidebar-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    padding: 10px;
    text-align: left;
    font-size: 0.7vw;
}
</style>
""",
    unsafe_allow_html=True,
)


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       Requisição de Api
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


async def get_data() -> tuple:
    """
    Obtém os dados da API.
    """
    date_now = datetime.now()
    now_ = date_now.strftime("%Y-%m-%d")
    urls = [
        APIUrl.URL_EFF.value,
        APIUrl.URL_INFO_IHM.value,
        APIUrl.URL_PROD.value,
        f"{APIUrl.URL_MAQ_INFO.value}?start={now_}&end={now_}",
    ]
    tasks = [fetch_api_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    eff = results[0]
    info_ihm = results[1]
    prod = results[2]
    info = results[3]
    return eff, info_ihm, prod, info


@st.cache_data(show_spinner="Obtendo dados", ttl=1200)
def get_df():
    """
    Obtém os dados da API.
    """
    eff, info_ihm, prod, info = asyncio.run(get_data())
    return eff, info_ihm, prod, info


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

if st.sidebar.button("Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
df_eff, df_maq_info_original, df_prod, df_info = get_df()

# ════════════════════════════════════════════════════════════════ Ajustar O Dataframe De Info ══ #

# Garantir que a data é um pandas Timestamp só com a data
df_maq_info_original.data_registro = pd.to_datetime(df_maq_info_original.data_registro).dt.date
df_eff.data_registro = pd.to_datetime(df_eff.data_registro).dt.date
df_prod.data_registro = pd.to_datetime(df_prod.data_registro).dt.date
df_info.data_registro = pd.to_datetime(df_info.data_registro).dt.date

# Filtrar pelo turno atual e data
df_maq_info_original = df_maq_info_original[(df_maq_info_original.data_registro == today)]
df_eff = df_eff[(df_eff.data_registro == today)]
df_prod = df_prod[(df_prod.data_registro == today)]
df_info = df_info[(df_info.data_registro == today)]

df_maq_info = df_maq_info_original.copy()
if turn_opt != "Dia Atual":
    df_maq_info = df_maq_info[(df_maq_info.turno == turn_opt)]
    df_eff = df_eff[(df_eff.turno == turn_opt)]
    df_prod = df_prod[(df_prod.turno == turn_opt)]
    df_info = df_info[(df_info.turno == turn_opt)]

# Filtrar pela linha
df_maq_info = df_maq_info[(df_maq_info.linha == line)].reset_index(drop=True)
df_maq_info_original = df_maq_info_original[(df_maq_info_original.linha == line)].reset_index(
    drop=True
)
df_eff = df_eff[(df_eff.linha == line)].reset_index(drop=True)
df_prod = df_prod[(df_prod.linha == line)].reset_index(drop=True)
df_info = df_info[(df_info.linha == line)].reset_index(drop=True)

# Se a coluna eficiencia estiver vazia, colocar zero
df_eff.eficiencia = df_eff.eficiencia.fillna(0)

# Obter o valor da eficiência
eff_value = round(df_eff.eficiencia.mean() * 100) if not df_eff.empty else 0

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

st.subheader(f"Linha: {line} / Máquina: {df_eff.maquina_id.iloc[0]}" if not df_eff.empty else None)
st.divider()

r1_col1, r1_col2, r1_col3 = st.columns([1, 4, 1])

# ═══════════════════════════════════════════════════════════════════════════════════ Coluna 1 ══ #
with r1_col1:
    # ── Gauge ────────────────────────────────────────────────────────────────────────────────── #
    with st.container():
        create_gauge_chart(IndicatorType.EFFICIENCY, eff_value, "line_gg_eff", True)

    # ── Status ───────────────────────────────────────────────────────────────────────────────── #
    _, turno_atual = get_date.get_this_turn()
    df_maq_info_status = df_maq_info_original[(df_maq_info_original.turno == turno_atual)]
    # Recuperar o status da última entrada de maq_info
    if turn == turn_opt:
        with st.container():
            status = df_maq_info_status.status.iloc[-1].capitalize()
            back_color = ColorsSTM.GREEN.value if status == "Rodando" else ColorsSTM.RED.value
            opt_1 = f"background-color: {back_color}; color: {ColorsSTM.LIGHT_GREY.value};"
            st.markdown(f"""<div class="card">{status}</div>""", unsafe_allow_html=True)

        if status != "Rodando":
            with st.container():
                df_maq_info_status.loc[df_maq_info_status.motivo == "Limpeza", "causa"] = "Limpeza"
                causa = df_maq_info_status.causa.iloc[-1]
                causa = causa if causa else "Não informado"
                st.markdown(f"""<div class="card2">{causa}</div>""", unsafe_allow_html=True)

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
                TEMPO = round((hora_final - hora_inicial).seconds / 60)
                # Ajustar tempo para uma string formatada no formato mm
                TEMPO = str(TEMPO).replace(".", ",")

                st.markdown(
                    f"""<div class="card2" style="font-size: 1.5vw;">{TEMPO} min</div>""",
                    unsafe_allow_html=True,
                )

# ═══════════════════════════════════════════════════════════════════════════════════ Coluna 2 ══ #
with r1_col2:
    c2_col_1, c2_col_2 = st.columns([1, 3])

    # ────────────────────────────────────────────────────────────────────────── Card Produção ── #
    with c2_col_1:
        producao = (
            df_prod.total_produzido.iloc[-1]
            if len(turn_opt) == 3
            else df_prod.total_produzido.sum()
        )
        producao = producao.clip(min=0)
        st.markdown(
            f"""<div class="card3">
            <p style="font-size: 0.7vw; text-align: left;
            padding-left: 0.5vw; margin-bottom: 0; margin-top: 10px;">Produto</p>
            <h1 style="font-size: 1.1vw;">{df_prod.produto.iloc[-1]}</h1>
            <p style="font-size: 0.7vw; text-align: left ;
            padding-left: 0.5vw ; margin-bottom: 0;">Produção de Bandejas</p>
            <h1 style="font-size: 2vw;">{producao}</h1>
            </div>""",
            unsafe_allow_html=True,
        )

    with c2_col_2:
        # ─────────────────────────────────────────────────────────────────────── Pareto Chart ── #
        # Separa apenas as paradas
        data_filtered = df_maq_info.copy()
        # Calcula o tempo de parada
        tempo_last_stop = round((now - pd.to_datetime(df_maq_info.iloc[-1].data_hora)).seconds / 60)
        # Insere este tempo na coluna tempo da última linha da tabela data_filtered
        data_filtered.loc[data_filtered.index[-1], "tempo"] = tempo_last_stop
        # Mantém apenas linhas onde o status é parada
        data_filtered = data_filtered[data_filtered.status == "parada"]
        # Onde problema e causa forem nulos, preencher com não apontado
        data_filtered.problema = data_filtered.problema.fillna("Não apontado")
        data_filtered.causa = data_filtered.causa.fillna("")
        # Se a causa for refeição, preencher o problema com refeição
        data_filtered.problema = data_filtered.problema.mask(
            data_filtered.motivo == "Parada Programada", data_filtered.causa
        )
        # Ordena o dataframe pelo tempo
        data_filtered = data_filtered.sort_values(by="tempo")

        alt_fig = (
            alt.Chart(data_filtered)
            .mark_bar(orient="horizontal", color="darkgray")
            .encode(
                y=alt.Y("problema", sort="-x", title="Problema", axis=alt.Axis()),
                x=alt.X("tempo", title="Tempo (minutos)"),
                tooltip=[
                    alt.Tooltip("problema", title="Problema"),
                    alt.Tooltip("causa", title="Causa"),
                    alt.Tooltip("tempo", title="Tempo"),
                ],
            )
        )
        if len(data_filtered) > 0:
            st.altair_chart(alt_fig, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────── Ciclos Chart ── #
    df_info.hora_registro = pd.to_datetime(df_info.hora_registro, format="%H:%M:%S")
    df_info_stops = df_info[df_info.status == "rodando"]
    media_ciclos = round(df_info_stops.ciclo_1_min.mean(), 2) if len(df_info_stops) > 0 else 0
    # Figura principal com os ciclos
    alt_fig_2 = (
        alt.Chart(df_info)
        .mark_line(color="darkgray")
        .encode(
            x=alt.X("hora_registro", title="Hora", axis=alt.Axis(format="%H:%M")),
            y=alt.Y("ciclo_1_min", title="Ciclos"),
        )
    )
    # Figura da linha da média
    alt_fig_2 += (
        alt.Chart(pd.DataFrame({"media_ciclos": [media_ciclos]}))
        .mark_rule(color="cadetblue")
        .encode(
            y=alt.Y("media_ciclos"), tooltip=[alt.Tooltip("media_ciclos", title="Média de Ciclos")]
        )
    )
    # Figura com marcação dos ciclos médios
    str_media = f"Média de Ciclos: {media_ciclos}"
    alt_fig_2 += (
        alt.Chart(pd.DataFrame({"Média de Ciclos": [media_ciclos]}))
        .mark_text(color="cadetblue", dy=-10, fontSize=12)
        .encode(y=alt.Y("Média de Ciclos"), text=alt.Text("Média de Ciclos"))
    )
    alt_fig_2 = alt_fig_2.properties(
        height=200,
    )

    st.divider()
    st.altair_chart(alt_fig_2, use_container_width=True)

    # ───────────────────────────────────────────────────────────────────────── Timeline Chart ── #
    timeline_data = df_maq_info.copy()

    # Convertendo a coluna data_hora para datetime e data_hora_final para datetime
    timeline_data.data_hora = pd.to_datetime(timeline_data.data_hora)
    timeline_data.data_hora_final = pd.to_datetime(timeline_data.data_hora_final)
    # Ajustar a data_hora_ final
    timeline_data.loc[timeline_data.index[-1], "data_hora_final"] = (
        now if (turn_opt == turn or len(turn_opt) > 3) else timeline_data.iloc[-1].data_hora_final
    )
    # Ajustar o tempo atual
    timeline_data.loc[timeline_data.index[-1], "tempo"] = (
        round((now - timeline_data.iloc[-1].data_hora).seconds / 60)
        if (turn_opt == turn or len(turn_opt) > 3)
        else timeline_data.iloc[-1].tempo
    )

    # Onde o status for rodando mudar o motivo para Rodando
    timeline_data.loc[timeline_data.status == "rodando", "motivo"] = "Rodando"
    # Preencher motivo nulo com não apontado
    timeline_data.motivo = timeline_data.motivo.fillna("Não apontado")
    timeline_data.causa = timeline_data.causa.fillna("")
    # Se a causa for refeição, preencher o problema com refeição
    timeline_data.motivo = timeline_data.motivo.mask(timeline_data.causa == "Refeição", "Refeição")
    motivos_presentes = timeline_data.motivo.unique()
    color_timeline = {motivo: COLOR_DICT[motivo] for motivo in motivos_presentes}

    # Criando um gráfico de timeline
    timeline_fig = (
        alt.Chart(timeline_data)
        .mark_bar()
        .encode(
            x=alt.X("data_hora:T", title="Hora", axis=alt.Axis(format="%H:%M")),
            x2="data_hora_final:T",
            y=alt.Y("turno:N", title="Turno"),
            color=alt.Color(
                "motivo:N",
                legend=alt.Legend(orient="bottom"),
                title="Motivos",
                scale=alt.Scale(
                    domain=list(color_timeline.keys()), range=list(color_timeline.values())
                ),
            ),
            tooltip=[
                alt.Tooltip("motivo:N", title="Motivo"),
                alt.Tooltip("causa:N", title="Causa"),
                alt.Tooltip("data_hora:T", title="Hora Inicial", format="%H:%M"),
                alt.Tooltip("data_hora_final:T", title="Hora Final", format="%H:%M"),
                alt.Tooltip("tempo", title="Tempo (minutos)"),
            ],
        )
    )

    st.altair_chart(timeline_fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════════ Coluna 3 ══ #
with r1_col3:
    # ─────────────────────────────────────────────────────────────────────── Metric - Rodando ── #
    with st.container():
        # Pegar a linha atual
        last_row = df_maq_info.iloc[-1]
        # Pegar o horário da última linha e calcular a diferença com o horário atual
        last_row_hour = pd.to_datetime(last_row.data_hora)

        # Calcular o tempo de parada em minutos
        tempo_last = round((now - last_row_hour).seconds / 60)

        # Calcular o tempo rodando em minutos
        tempo_rodando = df_maq_info[df_maq_info.status == "rodando"]
        tempo_rodando = round(tempo_rodando.tempo.sum())

        if last_row.status == "rodando" and (turn == last_row.turno or len(turn) > 3):
            tempo_rodando = tempo_rodando + tempo_last - 1

        st.metric("Tempo Total Rodando", tempo_rodando)

    # ──────────────────────────────────────────────────────────────────────── Metric - Parada ── #
    with st.container():
        # Calcular o tempo de parada em minutos
        tempo_parada = df_maq_info[df_maq_info.status == "parada"]
        tempo_parada = round(tempo_parada.tempo.sum())

        if last_row.status == "parada" and (turn == last_row.turno or len(turn) > 3):
            tempo_parada = tempo_parada + tempo_last - 1

        st.metric("Tempo Total Parada", tempo_parada)

    # ────────────────────────────────────────────────────────────────────────────────── Setup ── #
    with st.container():
        # Selecionar as linhas com motivo setup
        df_setup = df_maq_info[df_maq_info.motivo == "Setup"]

        # Soma o tempo de setup em minutos
        tempo_setup = df_setup.tempo.sum()

        st.metric("Tempo em Setup", tempo_setup)

# ═══════════════════════════════════════════ Tabelas ═══════════════════════════════════════════ #
st.divider()
with st.expander("Tabelas para conferência"):
    st.subheader("Tabela de Eficiência")
    st.write(df_eff)
    st.subheader("Tabela de Ocorrências")
    st.write(df_maq_info)
    st.subheader("Tabela de Produção")
    st.write(df_prod)

#    ┏━                                                                                    ━┓
#    ┃                                       Estilos                                        ┃
#    ┗━                                                                                    ━┛
st.markdown(
    """
<style>
.card {
    text-align: center;
    font-size: 1.8vw;
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
""",
    unsafe_allow_html=True,
)
