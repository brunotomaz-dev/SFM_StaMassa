"""Página de indicadores de eficiência, performance e reparo."""

import altair as alt
import pandas as pd
import streamlit as st

# from streamlit_option_menu import option_menu
import streamlit_antd_components as stc

# pylint: disable=import-error
from app.components import sfm_gauge as sfm_gg
from app.components import sfm_gauge_opt2 as sfm_gg2
from app.components.sfm_bar_eff import BarChartEff
from app.components.sfm_heatmap import create_heatmap_chart
from app.components.sfm_line import create_line_chart
from app.functions.indicators_playground import IndicatorsPlayground
from app.helpers.variables import TURNOS, ColorsSTM, IndicatorType
from streamlit_extras.metric_cards import style_metric_cards

ind_play = IndicatorsPlayground()
create_bar_chart_eff = BarChartEff().create_bar_chart_eff

# ================================== Visualizações - Sub-páginas ================================= #
SUB_OPT_1 = "Principal"
SUB_OPT_2 = "Análise Mensal"

# ================================================================================================ #
#                                            MENU WIDGET                                           #
# ================================================================================================ #

# with st.sidebar:
#     selected_page = option_menu(
#         "Visualização",
#         [SUB_OPT_1, SUB_OPT_2],
#         icons=["bi bi-graph-down", "bi bi-bar-chart-line-fill"],
#         menu_icon="cast",
#         default_index=0,
#     )

with st.sidebar:
    selected_page = stc.menu(
        [
            stc.MenuItem(SUB_OPT_1, icon="bi bi-graph-down"),
            stc.MenuItem(SUB_OPT_2, icon="bi bi-bar-chart-line-fill"),
        ]
    )


# ================================================================================================ #
#                                            NAV WIDGETS                                           #
# ================================================================================================ #
turn: str | None = None
fabrica: str | None = None
line_turn: str = "Turno"
motivo_problema: str | None = None

# =========================================== Principal ========================================== #
if selected_page == SUB_OPT_1:
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

# ============================================= Opt 2 ============================================ #
if selected_page == SUB_OPT_2:
    # Selectbox - Seleção de motivo ou problema para o gráfico de paradas
    motivo_problema = st.sidebar.selectbox("Apresentar paradas por:", ["Motivo", "Problema"])

# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #
history_ind = st.session_state.hist_ind if "hist_ind" in st.session_state else pd.DataFrame()
eficiencia = st.session_state.eficiencia if "eficiencia" in st.session_state else pd.DataFrame()
performance = st.session_state.performance if "performance" in st.session_state else pd.DataFrame()
reparo = st.session_state.reparos if "reparos" in st.session_state else pd.DataFrame()
stops = st.session_state.info_ihm if "info_ihm" in st.session_state else pd.DataFrame()

# Ajustar as datas para datetime
eficiencia["data_registro"] = pd.to_datetime(eficiencia["data_registro"])
performance["data_registro"] = pd.to_datetime(performance["data_registro"])
reparo["data_registro"] = pd.to_datetime(reparo["data_registro"])
stops["data_registro"] = pd.to_datetime(stops["data_registro"])

# Filtrar para manter apenas dados do mês corrente
current_period = eficiencia["data_registro"].dt.to_period("M").max()
eficiencia = eficiencia[eficiencia["data_registro"].dt.to_period("M") == current_period]
performance = performance[performance["data_registro"].dt.to_period("M") == current_period]
reparo = reparo[reparo["data_registro"].dt.to_period("M") == current_period]
stops = stops[stops["data_registro"].dt.to_period("M") == current_period]

# ==================================== Ajustes Dos Indicadores =================================== #
df_eff = ind_play.get_indicator(eficiencia, IndicatorType.EFFICIENCY, turn, line_turn, fabrica)
df_perf = ind_play.get_indicator(performance, IndicatorType.PERFORMANCE, turn, line_turn, fabrica)
df_rep = ind_play.get_indicator(reparo, IndicatorType.REPAIR, turn, line_turn, fabrica)

# Gauge - Valores dos indicadores do mês corrente
efficiency_actual = round(df_eff.eficiencia.dropna().mean())
performance_actual = round(df_perf.performance.dropna().mean())
repair_actual = round(df_rep.reparo.dropna().mean())


if selected_page == SUB_OPT_1:

    # Heatmap - Ajuste dos dataframes para a estrutura cartesiana para o heatmap
    df_eff_opt, days_eff, ref_eff = ind_play.create_heatmap_structure(
        df_eff.copy(), IndicatorType.EFFICIENCY
    )
    st.write(df_eff_opt)
    st.write(days_eff)
    st.write(ref_eff)
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

if selected_page == SUB_OPT_2:

    # Filtra removendo o status 'rodando'
    stops = stops[stops.status != "rodando"]

    # Filtra removendo o problema "Parada Planejada"
    stops = stops[stops.problema != "Parada Planejada"]

    # Preenche apenas os campos nulos de: problema, causa, equipamento e motivo com "Não Apontado"
    stops[["problema", "causa", "equipamento", "motivo"]] = stops[
        ["problema", "causa", "equipamento", "motivo"]
    ].fillna("Não Apontado")

    # Encontra o principal motivo de parada
    grouped = stops.groupby(motivo_problema.lower()).tempo.sum().reset_index()

    # Ordena por tempo decrescente
    grouped = grouped.sort_values(by="tempo", ascending=False).reset_index(drop=True)

    # Encontra o principal motivo de parada
    greater_motive = grouped[motivo_problema.lower()].iloc[0]

    # Se o principal motivo for "Não Apontado", pega o segundo maior
    if greater_motive == "Não Apontado":
        greater_motive = grouped[motivo_problema.lower()].iloc[1]

    # Mantém apenas as paradas com o principal motivo
    greater_motive = stops[stops[motivo_problema.lower()] == greater_motive]

    # Agrupa por causa e soma o tempo
    greater_motive = greater_motive.groupby("causa").tempo.sum().reset_index()

    # Ordena por tempo decrescente
    greater_motive = greater_motive.sort_values(by="tempo", ascending=False).reset_index(drop=True)

    # Pega as 10 maiores causas
    greater_motive = greater_motive.head(10)

    # Agrupar por motivo ou problema, de acordo com a seleção do usuário e somar o tempo
    top_stops = stops.groupby(motivo_problema.lower()).tempo.sum().reset_index()

    # Ordenar por tempo decrescente
    top_stops = top_stops.sort_values(by="tempo", ascending=False).reset_index(drop=True)

    # Ajusta para top 5 caso motivo_problema seja problema
    if motivo_problema == "Problema":
        top_stops = top_stops.head(10)

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

st.title("Shop Floor Management")
st.divider()

# =========================================== Principal ========================================== #
if selected_page == SUB_OPT_1:

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
if selected_page == SUB_OPT_2:

    r1_col1, r1_col2, r1_col3 = st.columns([1, 1, 1])

    with r1_col1:
        # with st.container(border=True):

        g1, g2, g3 = st.columns(3)
        with g1:
            sfm_gg2.create_gauge_chart(
                IndicatorType.EFFICIENCY, efficiency_actual, "opt1_eff_gauge", pos="top"
            )

        with g2:
            sfm_gg2.create_gauge_chart(
                IndicatorType.PERFORMANCE, performance_actual, "opt1_perf_gauge"
            )

        with g3:
            sfm_gg2.create_gauge_chart(
                IndicatorType.REPAIR, repair_actual, "opt1_rep_gauge", pos="top"
            )

    with r1_col2:
        alt_fig = (
            alt.Chart(top_stops)
            .mark_bar()
            .encode(
                x=alt.X(
                    motivo_problema.lower(),
                    sort="-y",
                    title=motivo_problema.capitalize(),
                    axis=alt.Axis(labelAngle=30, labelOverlap=False),
                ),
                y=alt.Y("tempo", title="Tempo (minutos)", axis=alt.Axis(format="~s")),
            )
        )

        st.altair_chart(alt_fig, use_container_width=True)

    with r1_col3:
        alt_fig_2 = (
            alt.Chart(greater_motive)
            .mark_bar()
            .encode(
                x=alt.X(
                    "causa",
                    sort="-y",
                    title="Causa",
                    axis=alt.Axis(labelAngle=30, labelOverlap=False),
                ),
                y=alt.Y("tempo", title="Tempo (minutos)", axis=alt.Axis(format="~s")),
            )
        )

        st.altair_chart(alt_fig_2, use_container_width=True)

    r2_col1, r2_col2 = st.columns([1, 2])

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

    with r2_col2:
        bar_eff = create_bar_chart_eff(eficiencia)
        st.plotly_chart(bar_eff, use_container_width=True)

    style_metric_cards(
        background_color=ColorsSTM.LIGHT_GREY.value,
        border_left_color="white",
        border_radius_px=10,
    )

    # =========================================== Table ========================================== #
    # Ordenar por data_registro e hora_registro
    table_stops = stops.sort_values(
        by=["data_registro", "hora_registro"], ascending=False
    ).reset_index(drop=True)

    # Remover colunas desnecessárias
    table_stops = table_stops.drop(columns=["status", "data_registro_ihm", "hora_registro"])

    # Ajustar a data para visualização
    table_stops.data_registro = pd.to_datetime(table_stops.data_registro).dt.strftime("%d/%m")

    # Ajustar a hora para visualização
    table_stops.hora_registro_ihm = pd.to_datetime(
        table_stops.hora_registro_ihm, format="%H:%M:%S.%f"
    ).dt.strftime("%H:%M")

    # Ajustar a matrícula do operador para visualização
    table_stops.operador_id = table_stops.operador_id.fillna(0).astype(int)
    table_stops.operador_id = table_stops.operador_id.astype(str).str.zfill(6)

    # Alterar onde o valor é 000000 para None
    table_stops.operador_id = table_stops.operador_id.replace("000000", None)

    # Ajustar o número da ordem de serviço para visualização
    table_stops.os_numero = table_stops.os_numero.fillna(0).astype(int)
    table_stops.os_numero = table_stops.os_numero.astype(str).str.zfill(6)

    # Alterar onde o valor é 000000 para None
    table_stops.os_numero = table_stops.os_numero.replace("000000", None)

    # Ajustar a data e hora da parada para visualização
    table_stops.data_hora = pd.to_datetime(table_stops.data_hora).dt.strftime("%d/%m - %H:%M")

    # Ajustar a data e hora do fim da parada para visualização
    table_stops.data_hora_final = pd.to_datetime(table_stops.data_hora_final).dt.strftime(
        "%d/%m - %H:%M"
    )

    # Renomear colunas
    table_stops.columns = table_stops.columns.str.replace("_", " ").str.title()
    table_stops = table_stops.rename(
        columns={
            "Fabrica": "Fábrica",
            "Maquina Id": "Máquina Id",
            "Data Registro": "Data",
            "Os Numero": "OS Número",
            "Hora Registro Ihm": "Hora do Apontamento",
            "S Backup": "Saída para Linha",
            "Data Hora": "Data e Hora da Parada",
            "Data Hora Final": "Data e Hora do Fim da Parada",
        }
    )
    with st.expander("Tabela de Ocorrências", expanded=False, icon=":material/table_rows:"):
        st.write(table_stops)
