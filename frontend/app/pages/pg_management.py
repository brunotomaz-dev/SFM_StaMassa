""" Módulo que contém a página de gestão. """

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# pylint: disable=import-error
from app.components.action_plan import action_plan
from app.functions.get_date import GetDate
from app.functions.perf_ciclo import performance_ciclo
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

# Dados da maquina e IHM
info_data = st.session_state.info_ihm if "info_ihm" in st.session_state else pd.DataFrame()

# Data inicial do dataframe
day_one = pd.to_datetime(info_data["data_registro"].min()).date()

# Data final do dataframe
day_last = pd.to_datetime(info_data["data_registro"].max()).date()

# Data do início e fim baseada no hoje.
yesterday = day_last - pd.Timedelta(days=1)

date_col, turn_col, line_col, fab_col = st.columns([0.15, 0.15, 0.60, 0.10])

# Seleção de data
date_choice_1, date_choice_2 = date_col.date_input(
    "Escolha a data",
    value=(max(FIRST_DAY.date(), day_one), min(yesterday, day_last)),
    min_value=day_one,
    max_value=TODAY,
    format="DD/MM/YYYY",
)

turn_choice = turn_col.selectbox(
    "Escolha o turno",
    options=[" ", "Matutino", "Vespertino", "Noturno"],
)

turn_filter = {
    " ": None,
    "Matutino": "MAT",
    "Vespertino": "VES",
    "Noturno": "NOT",
}[turn_choice]

fab_choice = fab_col.selectbox(
    "Escolha a fábrica",
    options=[" ", *info_data["fabrica"].unique()],
)

# Filtra pela fábrica
if fab_choice != " ":
    info_data = info_data[info_data["fabrica"] == fab_choice]

line_choice = line_col.multiselect(
    "Escolha as linhas",
    options=info_data["linha"].unique(),
    default=info_data["linha"].unique(),
)

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
info_ihm: pd.DataFrame = info_data.copy() if not info_data.empty else pd.DataFrame()
production: pd.DataFrame = (
    st.session_state.produção.copy() if "produção" in st.session_state else pd.DataFrame()
)

# Ajustar a data de registro
info_ihm["data_registro"] = pd.to_datetime(info_ihm["data_registro"])
production["data_registro"] = pd.to_datetime(production["data_registro"])

# Se necessário, filtrar pela data, se não mantêm apenas os dados do mês atual
info_ihm = info_ihm[
    (info_ihm["data_registro"].dt.date >= date_choice_1)
    & (info_ihm["data_registro"].dt.date <= date_choice_2)
]

# Filtrar pelo turno
if turn_filter:
    info_ihm = info_ihm[info_ihm["turno"] == turn_filter]
    production = production[production["turno"] == turn_filter]


# Filtrar as linhas escolhidas
info_ihm = info_ihm[info_ihm["linha"].isin(line_choice)]

# Filtrar pela data escolhida
production = production[
    (production["data_registro"].dt.date >= date_choice_1)
    & (production["data_registro"].dt.date <= date_choice_2)
]

# Filtrar as linhas escolhidas
production = production[production["linha"].isin(line_choice)]

# Manter apenas a data
info_ihm["data_registro"] = info_ihm["data_registro"].dt.date
production.data_registro = production.data_registro.dt.date


@st.cache_data()
def df_info_adjustment(dataframe: pd.DataFrame, group: bool = False) -> pd.DataFrame:
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
    df["hora_registro"] = df["hora_registro"].astype(str).str.extract(r"(\d{2}:\d{2}:\d{2})")[0]
    df["hora_registro"] = pd.to_datetime(df["hora_registro"], format="%H:%M:%S").dt.time
    df["hora_registro_ihm"] = (
        df["hora_registro_ihm"].astype(str).str.extract(r"(\d{2}:\d{2}:\d{2})")[0]
    )
    df["hora_registro_ihm"] = pd.to_datetime(df["hora_registro_ihm"], format="%H:%M:%S").dt.time

    # Adicionar Refeição como motivo onde a causa é Refeição e o motivo for Parada Programada
    mask = (df["motivo"] == "Parada Programada") & (df["causa"] == "Refeição")
    df["motivo"] = np.where(mask, "Refeição", df["motivo"])

    if group:
        # Agrupar os dados
        df_grouped = (
            df.groupby(["linha", "data_registro", "turno", "motivo"], observed=False)
            .agg({"tempo": "sum", "hora_registro": "first"})
            .reset_index()
        )

        # Ordenar pela linha e motivo
        df_grouped = df_grouped.sort_values(by=["linha", "motivo"]).reset_index(drop=True)

        return df_grouped

    return df


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

    # Voltar o dataframe para o formato original
    df = df.melt(id_vars="linha", var_name="motivo", value_name="tempo")

    programado = df[df["motivo"].isin(["Refeição", "Limpeza", "Parada Programada"])].copy()
    n_programado = df[
        ~df["motivo"].isin(["Refeição", "Limpeza", "Parada Programada", "Rodando"])
    ].copy()
    completo = n_programado.groupby("linha", observed=False).agg({"tempo": "sum"}).reset_index()

    return df, programado, n_programado, completo


bar_df = df_info_adjustment(info_ihm, group=True)
bar_full_df = df_info_adjustment(info_ihm)

echart_df, programado_df, n_programado_df, geral_n_programado_df = df_echart_adjustment(bar_df)

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GRÁFICO DE BARRAS DO ECHART ━━ #
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
        "title": {"text": "Gráfico Ocorrências", "left": "center"},
        "tooltip": {
            "trigger": "item",
            "axisPointer": {"type": "shadow"},
            "confine": True,
        },
        "legend": {
            "data": [*bar_df.motivo.unique().tolist(), "Paradas Não Programadas"],
            "bottom": "0%",
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "20%", "top": "10%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": bar_df.linha.unique().tolist(),
            "name": "Linhas",
            "nameLocation": "center",
            "nameGap": 20,
        },
        "yAxis": {"type": "value", "name": "Tempo (min)", "nameLocation": "center", "nameGap": 50},
        "series": series,
    }

    # Plot do Gráfico
    st_echarts(options=options)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GRÁFICO DE BARRAS ━━ #
with st.container(border=True):
    # Converter a coluna hora_registro para string no formato %H:%M:%S
    bar_df["hora_registro"] = bar_df["hora_registro"].apply(lambda x: x.strftime("%H:%M"))

    # ===================================================================================== Plotly #
    # Criar gráfico de barras com Plotly
    # bar_fig = px.bar(
    #     bar_df,
    #     x="linha",
    #     y="tempo",
    #     color="motivo",
    #     color_discrete_map=COLOR_DICT,
    #     custom_data=["data_registro", "hora_registro", "motivo", "tempo"],
    #     height=400,
    # )

    # # Configurar layout
    # bar_fig.update_layout(
    #     barmode="relative",
    #     showlegend=True,
    #     legend=dict(
    #         orientation="h",
    #         yanchor="bottom",
    #         y=1.02,
    #         xanchor="left",
    #         x=0,
    #         title="Motivos",
    #     ),
    #     margin=dict(t=50, l=10, r=10, b=10),
    #     yaxis_title="Tempo (min)",
    #     xaxis_title="Linhas",
    # )

    # # Configurar hover template
    # bar_fig.update_traces(
    #     hovertemplate="<b>Data:</b> %{customdata[0]}<br>"
    #     + "<b>Hora:</b> %{customdata[1]}<br>"
    #     + "<b>Motivo:</b> %{customdata[2]}<br>"
    #     + "<b>Tempo:</b> %{customdata[3]} min<extra></extra>"
    # )

    # # Exibir gráfico
    # st.plotly_chart(bar_fig, use_container_width=True)

    # ===================================================================================== Echart #
    lines = bar_df["linha"].unique().tolist()
    motivos = bar_df["motivo"].unique().tolist()

    # Criar series para cada motivo com valores convertidos
    series_data = []
    for motivo in motivos:
        data = []
        for line in lines:
            tempo = float(
                bar_df[(bar_df["linha"] == line) & (bar_df["motivo"] == motivo)]["tempo"].sum()
            )
            data.append(tempo)

        series_data.append(
            {
                "name": motivo,
                "type": "bar",
                "stack": "total",
                "data": data,
                "itemStyle": {"color": COLOR_DICT.get(motivo, "#000000")},
            }
        )

    # Configurar opções do gráfico
    options = {
        "title": {"text": "Gráfico Yamazumi", "left": "center"},
        "tooltip": {
            "trigger": "item",
            "axisPointer": {"type": "shadow"},
            "confine": True,
        },
        "legend": {"orient": "horizontal", "bottom": "0%", "data": motivos},
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "10%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": lines,
            "name": "Linhas",
            "nameLocation": "center",
            "nameGap": 20,
        },
        "yAxis": {"type": "value", "name": "Tempo (min)", "nameLocation": "center", "nameGap": 50},
        "series": series_data,
    }

    # Renderizar gráfico
    st_echarts(
        options=options,
        height="400px",
    )

# ====================================================================================== Bar Chart #
stops = bar_full_df.copy()

# Soma o tempo total do período
tempo_total = stops.tempo.sum()
# st.write(stops)
# st.write(tempo_total)

pc_tempo, pc_cycles = performance_ciclo(
    stops, date_choice_1, date_choice_2, turn_filter, line_choice
)

# st.write(pc_tempo)
# st.write(pc_cycles)

# Remove o que não é necessário
stops = stops[
    ~stops.motivo.isin(
        ["Rodando", "Parada Programada", "Não apontado", "Refeição", "Saída para Backup", "Limpeza"]
    )
]
# Agrupa por motivo de parada
top_stops = (
    stops.groupby("motivo", observed=False)
    .tempo.sum()
    .reset_index()
    .sort_values(by="tempo", ascending=False)
)
# st.write(top_stops)

# Encontra o principal motivo
primary_motive = top_stops["motivo"].iloc[0]
secondary_motive = top_stops["motivo"].iloc[1]
third_motive = top_stops["motivo"].iloc[2]
# Dataframe com apenas o principal motivo
top_problems = stops[stops["motivo"] == primary_motive]
secondary_problems = stops[stops["motivo"] == secondary_motive]
third_problems = stops[stops["motivo"] == third_motive]


# Agrupa pela causa
def group_by_causa(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os dados por causa e problema, somando o tempo.

    Args:
        df (pd.DataFrame): DataFrame de entrada.

    Returns:
        pd.DataFrame: DataFrame agrupado por causa e problema.
    """
    df = df.copy()
    if df.motivo.unique() == "Manutenção":
        df.causa = np.where(
            df.causa.isin(["Realizar análise de falha", "Necessidade de análise"]),
            df.problema,
            df.causa,
        )
    df = (
        df.groupby("causa", observed=False)
        .tempo.sum()
        .reset_index()
        .sort_values(by="tempo", ascending=False)
    )
    return df


top_problems = group_by_causa(top_problems)
secondary_problems = group_by_causa(secondary_problems)
third_problems = group_by_causa(third_problems)


def get_percentual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula o percentual de cada valor em relação ao tempo total.

    Args:
        df (pd.DataFrame): DataFrame de entrada.

    Returns:
        pd.DataFrame: DataFrame com a coluna percentual adicionada.
    """
    df["percentual"] = (df.tempo / tempo_total * 100).round(2)
    df = df.sort_values(by="percentual", ascending=False)
    return df


top_stops = get_percentual(top_stops)
top_problems = get_percentual(top_problems)
secondary_problems = get_percentual(secondary_problems)
third_problems = get_percentual(third_problems)

top_mot_col, top_cause_col = st.columns(2)
sec_cause_col, third_cause_col = st.columns(2)


# Preparar dados


def get_cause_percent_colors(df: pd.DataFrame, motive: str) -> tuple:
    """
    Prepara os dados de causa, percentual e cores para o gráfico de barras.

    Args:
        df (pd.DataFrame): DataFrame com os dados.
    """
    df = df.head(5)
    cause = df["causa"].tolist()
    percent = df["percentual"].tolist()
    colors = [COLOR_DICT.get(motive)] * len(cause)

    return cause, percent, colors


motivos = top_stops["motivo"].tolist()
valores = top_stops["percentual"].tolist()
cores_m = [COLOR_DICT.get(motivo, "#000000") for motivo in motivos]
top_cause, top_value, top_color = get_cause_percent_colors(top_problems, primary_motive)
sec_cause, sec_value, sec_color = get_cause_percent_colors(secondary_problems, secondary_motive)
third_cause, third_value, third_color = get_cause_percent_colors(third_problems, third_motive)


def create_line_echart(
    data_nome: list[str],
    data_values: list[float],
    cores: list[str],
    title: str,
):
    """
    Função para criar um gráfico de linhas com echart.

    Args:
        data_nome (list[str]): Lista com os nomes dos dados.
        valores (list[float]): Lista com os valores dos dados.
        cores (list[str]): Lista com as cores dos dados.
        title (str): Título do gráfico.

    Returns:
        None
    """

    # Configurar opções do gráfico
    options_echart = {
        "tooltip": {"trigger": "item", "formatter": "{b}: {c}%", "axisPointer": {"type": "shadow"}},
        "legend": {"bottom": "0%"},
        "grid": {"left": "7%", "right": "5%", "bottom": "10S%", "top": "10%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": data_nome,
            "axisLabel": {
                "rotate": 0,  # Remove rotação
                "interval": 0,
                "width": 100,  # Largura máxima antes da quebra
                "overflow": "break",  # Quebra o texto
                "lineHeight": 15,  # Altura da linha
            },
        },
        "yAxis": {
            "type": "value",
            "name": "Tempo (%)",
            "nameLocation": "center",
            "nameGap": 35,
        },
        "title": {"text": title, "left": "center"},
        "series": [
            {
                "data": [
                    {
                        "value": val,
                        "itemStyle": {"color": cores[0] if len(cores) == 1 else cor},
                    }
                    for val, cor in zip(
                        data_values,
                        cores,
                    )
                ],
                "type": "bar",
                "label": {"show": True, "position": "top", "formatter": "{c}%", "fontSize": 12},
            }
        ],
    }

    st_echarts(
        options=options_echart,
        height="400px",
    )


# Renderizar gráfico
with top_mot_col.container(border=True):
    create_line_echart(motivos, valores, cores_m, "Principais Motivos de Parada")
with top_cause_col.container(border=True):
    create_line_echart(
        top_cause, top_value, top_color, f"Principais Causas de {primary_motive.title()}"
    )
with sec_cause_col.container(border=True):
    create_line_echart(
        sec_cause,
        sec_value,
        sec_color,
        f"Principais Causas de {secondary_motive.title()}",
    )
with third_cause_col.container(border=True):
    create_line_echart(
        third_cause,
        third_value,
        third_color,
        f"Principais Causas de {third_motive.title()}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HISTOGRAM ━━ #
# Colunas de Histograma e Icicle

histogram_df = bar_df.copy()
# Remover o motivo rodando e parada programada
histogram_df = histogram_df[
    ~histogram_df.motivo.isin(
        ["Rodando", "Parada Programada", "Não apontado", "Saída para Backup", "Limpeza", "Refeição"]
    )
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

histogram_df = histogram_df.sort_values(by="count_motivo", ascending=False)
histogram_df.mean_tempo = histogram_df.mean_tempo.round(0)


with st.container(border=True):
    options = {
        "title": {
            "text": "Tempo Total de Paradas x Tempo Médio de Paradas x Quantidade de Paradas",
            "left": "center",
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"},
            "confine": True,
        },
        "legend": {"data": ["Tempo Total", "Tempo Médio"], "top": "7%"},
        "grid": {"left": "3%", "right": "4%", "bottom": "5%", "top": "10%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": histogram_df["count_motivo"].tolist(),
            "name": "Quantidade de Ocorrências",
            "nameLocation": "center",
            "nameGap": 30,
        },
        "yAxis": [
            {
                "type": "value",
                "name": "Tempo Total (min)",
                "position": "left",
            },
            {
                "type": "value",
                "name": "Tempo Médio (min)",
                "position": "right",
            },
        ],
        "series": [
            {
                "name": "Tempo Total",
                "type": "bar",
                "data": [
                    {
                        "value": row["sum_tempo"],
                        "itemStyle": {"color": COLOR_DICT.get(row["motivo"], "#000000")},
                        "count": row["count_motivo"],
                    }
                    for _, row in histogram_df.iterrows()
                ],
                "label": {"show": True, "position": "top", "formatter": "{c}"},
            },
            {
                "name": "Tempo Médio",
                "type": "line",
                "yAxisIndex": 1,
                "data": [
                    {
                        "value": row["mean_tempo"],
                        "count": row["count_motivo"],
                        "itemStyle": {"color": COLOR_DICT.get(row["motivo"], "#000000")},
                    }
                    for _, row in histogram_df.iterrows()
                ],
                "lineStyle": {
                    "color": "#fff",
                    "type": "dashed",
                    "width": 1,
                },
                "label": {"show": False, "position": "top", "formatter": "{c}"},
            },
        ],
    }

    # Renderizar gráfico
    st_echarts(options=options, height="483px")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ CHART ICICLE ━━ #
with st.container(border=True):

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

    opt_choice = st.radio(
        "Opções de Ajuste", ["Motivo", "Equipamento", "Linha", "Problema"], horizontal=True
    )

    options_path = {
        "Motivo": [
            "motivo",
            "turno",
            "equipamento",
            "problema",
            "causa",
        ],
        "Equipamento": [
            "equipamento",
            "turno",
            "motivo",
            "problema",
            "causa",
        ],
        "Linha": [
            "linha",
            "turno",
            "problema",
            "causa",
            "motivo",
            "equipamento",
        ],
        "Problema": [
            "problema",
            "turno",
            "causa",
            "linha",
            "motivo",
            "equipamento",
        ],
    }

    # Figura
    ice_fig = px.icicle(
        icicle_df,
        path=[px.Constant(f"Paradas por {opt_choice}"), *options_path[opt_choice]],
        values="tempo",
        color="motivo",
        color_discrete_map=COLOR_DICT,
    )

    # Atualizar layout para remover hover
    # ice_fig.update_traces(hovertemplate=None)

    # Personalizar o hovertemplate
    ice_fig.update_traces(hovertemplate="<b>%{label}</b><br>Tempo: %{value} min<extra></extra>")

    # Atualizar layout
    ice_fig.update_layout(
        margin=dict(t=50, b=10, l=10, r=10),
        title=dict(
            text="Gráfico Paradas por Blocos",
            x=0.5,  # Centraliza o título (0.5 = meio)
            xanchor="center",  # Ancora o título no centro
        ),
    )
    # Plot
    st.plotly_chart(ice_fig, use_container_width=True)

# ================================================================================================ #
#                                              TABELAS                                             #
# ================================================================================================ #

# ================================================================================= Tabelas Gerais #
with st.expander("Tabelas"):
    # Manter apenas as colunas necessárias
    production = production[["data_registro", "linha", "turno", "produto", "total_produzido"]]

    production.total_produzido = production.total_produzido.clip(lower=0)
    production.total_produzido = production.total_produzido

    # Renomear as colunas de data e produção
    production = production.rename(
        columns={
            "data_registro": "Data",
            "turno": "Turno",
            "produto": "Produto",
            "total_produzido": "Produção",
            "linha": "Linha",
        }
    )

    # Categorias na ordem desejada
    turno_order = ["NOT", "MAT", "VES"]

    # Converter "Turno" para categoria com a ordem especificada
    production["Turno"] = pd.Categorical(production["Turno"], categories=turno_order, ordered=True)

    # Ordenar os valores
    production = production.sort_values(by=["Data", "Linha", "Turno", "Produto"])

    # Agrupar os dados por data e turno e produto
    df_production_turn = (
        production.groupby(["Data", "Turno", "Produto"], observed=False)
        .agg({"Produção": "sum"})
        .sort_values(by=["Data", "Produto", "Turno"])
        .reset_index()
    )

    # Remover onde a produção for 0
    df_production_turn = df_production_turn[df_production_turn["Produção"] > 0]

    # Agrupar os dados por dia e produto
    df_production_day = (
        production.groupby(["Data", "Produto"], observed=False)
        .agg({"Produção": "sum"})
        .reset_index()
    )

    # Remover onde a produção for 0
    df_production_day = df_production_day[df_production_day["Produção"] > 0]

    # Usar styler para formatar o total produzido
    production = production.style.format(thousands=".", decimal=",", precision=2)
    df_production_turn = df_production_turn.style.format(thousands=".", decimal=",", precision=2)
    df_production_day = df_production_day.style.format(thousands=".", decimal=",", precision=2)

    # Tabela de Produção
    prod_col, prod_turn_col, prod_day_col = st.columns([1.4, 1.2, 1.07])
    prod_col.write("##### Produção por linha")
    prod_col.dataframe(production, hide_index=True, use_container_width=True)
    prod_turn_col.write("##### Produção por turno")
    prod_turn_col.dataframe(df_production_turn, hide_index=True, use_container_width=True)
    prod_day_col.write("##### Produção por dia")
    prod_day_col.dataframe(df_production_day, hide_index=True, use_container_width=True)


# ================================================================================== Plano De Ação #
st.divider()
action_plan(date_choice_1, date_choice_2)
