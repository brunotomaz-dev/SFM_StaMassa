""" Módulo que contém a página de gestão. """

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# pylint: disable=import-error
from app.components.action_plan import action_plan
from app.functions.get_date import GetDate
from app.helpers.variables import COLOR_DICT
from streamlit_echarts import st_echarts

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Style
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GLOBAL VARIABLES ━━ #

get_date = GetDate()

TODAY = get_date.get_today()
FIRST_DAY, LAST_DAY = get_date.get_this_month()

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                            Sidebar
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Título
st.sidebar.title("Configurações")

# Data do início e fim baseada no hoje.
yesterday = TODAY - pd.Timedelta(days=1)

# Seleção de data
date_choice = st.sidebar.date_input(
    "Escolha a data", value=None, min_value=FIRST_DAY, max_value=yesterday, format="DD/MM/YYYY"
)

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
info_ihm = st.session_state.info_ihm

# Ajustar a data de registro
info_ihm["data_registro"] = pd.to_datetime(info_ihm["data_registro"]).dt.date

# Se necessário, filtrar pela data
if date_choice:
    info_ihm = info_ihm[info_ihm["data_registro"] == date_choice]


@st.cache_data()
def df_info_adjustment(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Função para ajustar os dados da tabela de informações."""
    df = dataframe.copy()

    # Ajustar o Motivo para quando está rodando no status
    df["motivo"] = np.where(df["status"] == "rodando", "Rodando", df["motivo"])

    # Preenche com Não Apontado onde o motivo estiver vazio
    df["motivo"] = df["motivo"].fillna("Não apontado")

    # Ajustar as datas para o formato correto
    df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date
    df["data_registro_ihm"] = pd.to_datetime(df["data_registro_ihm"]).dt.date

    # Ajustar o horário para o formato correto
    df["hora_registro"] = pd.to_datetime(df["hora_registro"], format="%H:%M:%S.%f").dt.time
    df["hora_registro_ihm"] = pd.to_datetime(df["hora_registro_ihm"], format="%H:%M:%S.%f").dt.time

    # Adicionar Refeição como motivo onde a causa é Refeição e o motivo for Parada Programada
    mask = (df["motivo"] == "Parada Programada") & (df["causa"] == "Refeição")
    df["motivo"] = np.where(mask, "Refeição", df["motivo"])

    # Agrupar os dados
    df_grouped = (
        df.groupby(["linha", "data_registro", "turno", "motivo"], observed=False)
        .agg({"tempo": "sum", "hora_registro": "first"})
        .reset_index()
    )

    # Ordenar pela linha e motivo
    df_grouped = df_grouped.sort_values(by=["linha", "motivo"]).reset_index(drop=True)

    return df_grouped


@st.cache_data()
def df_echart_adjustment(dataframe: pd.DataFrame) -> tuple:
    """Função para ajustar os dados da tabela de informações."""
    df = dataframe.copy()

    # Calcular o tempo
    df = df.groupby(["linha", "motivo"], observed=False).agg({"tempo": "sum"}).reset_index()

    # Pivotar o dataframe para ter os motivos como colunas
    df = df.pivot_table(
        index="linha", columns="motivo", values="tempo", fill_value=0, observed=False
    ).reset_index()

    # Meltar o dataframe
    df = df.melt(id_vars="linha", var_name="motivo", value_name="tempo")

    programado = df[df["motivo"].isin(["Refeição", "Limpeza", "Parada Programada"])].copy()
    n_programado = df[
        ~df["motivo"].isin(["Refeição", "Limpeza", "Parada Programada", "Rodando"])
    ].copy()
    completo = n_programado.groupby("linha", observed=False).agg({"tempo": "sum"}).reset_index()

    return df, programado, n_programado, completo


bar_df = df_info_adjustment(info_ihm)
echart_df, programado_df, n_programado_df, geral_n_programado_df = df_echart_adjustment(bar_df)

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GRAFICO DE BARRAS DO ECHART ━━ #
with st.container(border=True):
    # Criação da série de dados
    series = [
        {
            "name": "Rodando",
            "type": "bar",
            "emphasis": {"focus": "series"},
            "data": echart_df[echart_df["motivo"] == "Rodando"].tempo.tolist(),
            "itemStyle": {"color": COLOR_DICT["Rodando"]},
            "barMaxWidth": 25,
        },
    ]
    # Adição das paradas programadas
    for motivo_programada in programado_df["motivo"].unique():
        series.append(
            {
                "name": motivo_programada,
                "type": "bar",
                "emphasis": {"focus": "series"},
                "stack": "programada",
                "data": programado_df[programado_df["motivo"] == motivo_programada].tempo.tolist(),
                "itemStyle": {"color": COLOR_DICT[motivo_programada]},
                "barMaxWidth": 25,
            }
        )

    # Barra Geral de paradas não programadas
    series.append(
        {
            "name": "Paradas Não Programadas",
            "type": "bar",
            "emphasis": {"focus": "series"},
            "data": geral_n_programado_df.tempo.tolist(),
            "itemStyle": {"color": "grey"},
            "barMaxWidth": 25,
            "markLine": {
                "lineStyle": {"type": "dashed"},
                "data": [[{"type": "min"}, {"type": "max"}]],
            },
        }
    )

    # Adição das paradas não programadas
    for motivo_n_programado in n_programado_df["motivo"].unique():
        series.append(
            {
                "name": motivo_n_programado,
                "type": "bar",
                "emphasis": {"focus": "series"},
                "stack": "n_programada",
                "data": n_programado_df[
                    n_programado_df["motivo"] == motivo_n_programado
                ].tempo.tolist(),
                "itemStyle": {"color": COLOR_DICT[motivo_n_programado]},
                "barMaxWidth": 4,
            }
        )

    # Criação das Opções do Echart
    options = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "confine": True,
        },
        "legend": {
            "data": [*bar_df.motivo.unique().tolist(), "Paradas Não Programadas"],
        },
        "xAxis": {
            "type": "category",
            "data": bar_df.linha.unique().tolist(),
            "name": "Linhas",
            "nameLocation": "center",
            "nameGap": 20,
        },
        "yAxis": {"type": "value", "name": "Tempo (min)", "nameLocation": "center", "nameGap": 50},
        "series": series,
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "top": "20%", "containLabel": True},
    }

    # Plot do Gráfico
    st_echarts(options=options)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GRÁFICO DE BARRAS ━━ #
with st.container(border=True):
    bar_fig = (
        alt.Chart(bar_df)
        .mark_bar()
        .encode(
            x=alt.X("linha:N", title="Linhas"),
            y=alt.Y("tempo:Q", title="Tempo (min)", stack="normalize"),
            color=alt.Color(
                "motivo:N",
                scale=alt.Scale(domain=list(COLOR_DICT.keys()), range=list(COLOR_DICT.values())),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("data_registro:T", title="Data de Registro"),
                alt.Tooltip("hora_registro:T", title="Hora de Registro", format="%H:%M"),
                alt.Tooltip("motivo:N", title="Motivo"),
                alt.Tooltip("tempo:Q", title="Tempo (min)"),
            ],
        )
        .properties(padding={"left": 10, "right": 10, "top": 5, "bottom": 0})
    )

    st.altair_chart(bar_fig, use_container_width=True)

# Colunas de Histograma e Icicle
col_hist, col_icicle = st.columns([1, 2])
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HISTOGRAM ━━ #
with col_hist.container(border=True):
    histogram_df = bar_df.copy()
    # Remover o motivo rodando e parada programada
    histogram_df = histogram_df[
        ~histogram_df.motivo.isin(["Rodando", "Parada Programada", "Não apontado"])
    ]

    # Agrupar os dados por motivo para calcular o tempo médio e somar o tempo
    histogram_df = (
        histogram_df.groupby("motivo", observed=False)
        .agg(
            count_motivo=("motivo", "size"),
            sum_tempo=("tempo", "sum"),
            mean_tempo=("tempo", "mean"),
        )
        .reset_index()
    )

    histogram_fig = (
        alt.Chart(histogram_df)
        .mark_bar()
        .encode(
            x=alt.X("count_motivo:Q", bin=alt.Bin(maxbins=12), title="Quantidade de Ocorrências"),
            xOffset="motivo:N",
            y=alt.Y("sum_tempo:Q", title="Soma do Tempo (min)"),
            color=alt.Color(
                "motivo:N",
                scale=alt.Scale(domain=list(COLOR_DICT.keys()), range=list(COLOR_DICT.values())),
                legend=None,  # Remover a legenda, se necessário
            ),
            tooltip=[
                alt.Tooltip("motivo:N", title="Motivo"),
                alt.Tooltip("count_motivo:Q", title="Quantidade de Ocorrências"),
                alt.Tooltip("sum_tempo:Q", title="Soma do Tempo (min)"),
                alt.Tooltip("mean_tempo:Q", title="Tempo Médio (min)", format=".0f"),
            ],
        )
        .properties(height=400, padding={"left": 10, "right": 10, "top": 5, "bottom": 0})
    )

    st.altair_chart(histogram_fig, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ CHART ICICLE ━━ #
with col_icicle.container(border=True):
    # Definir o df
    icicle_df = info_ihm.copy()

    # Remover motivos de parada programada e não apontado
    icicle_df = icicle_df[
        ~icicle_df.motivo.isin(["Parada Programada", "Não apontado", "Saída para Backup"])
    ]

    # Manter apenas 'status' parada
    icicle_df = icicle_df[icicle_df.status == "parada"]

    # Manter apenas onde há um motivo
    icicle_df = icicle_df[icicle_df.motivo.notnull()]

    # Preencher onde o equipamento for nulo com ""
    icicle_df.equipamento = icicle_df.equipamento.fillna("Linha inteira")
    icicle_df.problema = icicle_df.problema.fillna("")
    icicle_df.causa = icicle_df.causa.fillna("Sem causa informada")

    # Figura
    ice_fig = px.icicle(
        icicle_df,
        path=[
            px.Constant("Paradas por motivo"),
            "motivo",
            "turno",
            "equipamento",
            "problema",
            "causa",
        ],
        values="tempo",
        color="motivo",
        color_discrete_map=COLOR_DICT,
        height=407,
    )

    # Atualizar layout para remover hover
    ice_fig.update_traces(hovertemplate=None)

    # Atualizar layout
    ice_fig.update_layout(
        margin=dict(t=20, b=10, l=10, r=10),
    )
    # Plot
    st.plotly_chart(ice_fig, use_container_width=True)

# ================================================================================== Plano De Ação #
st.divider()
action_plan()
