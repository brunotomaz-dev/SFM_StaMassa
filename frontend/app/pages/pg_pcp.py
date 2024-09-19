import asyncio
from enum import Enum

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_antd_components as stc

# pylint: disable=E0401
from app.api.requests_ import get_api_data
from app.api.urls import APIUrl
from app.functions.get_date import GetDate
from app.functions.production_adj import adjust_pao

get_date = GetDate()

class PageSelection(Enum):
    MASSA = "Massa"
    PASTA = "Pasta"
    PRODUCAO_PAES = "Produção de Pães"

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       Requisição de API
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# Função geral para obter os dados da API
async def get_data(url: str, start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """
    Obtém os dados da API.
    """
    url = f"{url}?start={start}&end={end}" if start and end else url
    data = await get_api_data(url)
    return data

# Teste de dados
async def get_all_data() -> tuple:
    urls = [
        APIUrl.URL_MASSA.value,
        APIUrl.URL_PASTA.value,
        APIUrl.URL_MASSA_WEEK.value,
        APIUrl.URL_PASTA_WEEK.value,
        APIUrl.URL_CAIXAS_CF.value,
    ]
    tasks = [get_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    massa = results[0]
    pasta = results[1]
    massa_week = results[2]
    pasta_week = results[3]
    caixas_cf = results[4]
    return massa, pasta, massa_week, pasta_week, caixas_cf

@st.cache_data(show_spinner="Obtendo dados", ttl=60000)
def get_df():
    massa, pasta, massa_week, pasta_week, caixas_cf = asyncio.run(get_all_data())
    return massa, pasta, massa_week, pasta_week, caixas_cf

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                            Sidebar
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Páginas para exibição
with st.sidebar:
    pg_selection = stc.menu(
        [
            stc.MenuItem(PageSelection.MASSA.value, icon="bi bi-graph-up"),
            stc.MenuItem(PageSelection.PASTA.value, icon="bi bi-graph-up"),
            stc.MenuItem(PageSelection.PRODUCAO_PAES.value, icon="bi bi-box-seam"),
        ]
    )

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

df_massa, df_pasta, df_massa_week, df_pasta_week, df_caixas_cf = get_df()

# Colunas de massa que se repetem
massa_columns = [
    "Turno",
    "Fábrica",
    "Batidas Cheias(qtd)",
    "Batidas Cheias(Peso)",
    "Batidas Reprocesso(qtd)",
    "Batidas Reprocesso(Peso)",
    "Batidas Bolinha(qtd)",
    "Batidas Bolinha(Peso)",
    "Baguete Total(un)",
    "Bolinha Total(un)",
]

# Renomear colunas
df_massa.columns = [
    "Data",
    *massa_columns,
]
df_massa_week.columns = [
    "Ano",
    "Semana",
    "Data Inicial",
    *massa_columns,
]

# Ajustar o formato da coluna "Data"
df_massa["Data"] = pd.to_datetime(df_massa["Data"]).dt.date
df_massa_week["Data Inicial"] = pd.to_datetime(df_massa_week["Data Inicial"]).dt.date

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
st.header("PCP")

#    ╭─                                                                                    ─╮
#    │                                Visualização de Massa                                 │
#    ╰─                                                                                    ─╯

if pg_selection == PageSelection.MASSA.value:
    st.subheader("Análise de Massa - Produzido x Consumido")

    # ─────────────────────────────────────────────────────────────────────── Análise De Massa ── #
    # Ajustar a produção de pães
    production = adjust_pao(df_caixas_cf)

    # Máscara para selecionar pão bolinha
    mask = production["Produto"].str.contains("BOL ")

    # Adicionar a produção de Bolinha a uma coluna
    production["Bolinha"] = mask.astype(int) * production["Pães"]
    # Remover a produção de bolinha da coluna de pão
    production["Baguete"] = production["Pães"].sub(production["Bolinha"])

    # Agrupar por ano, semana e fábrica
    production = (production
                  .groupby(["Ano", "Semana", "Data Inicial", "Fábrica"])
                  .sum()
                  .drop(columns="Produto")
                  .reset_index()
                  )

    massa_week = (df_massa_week
                  .groupby(["Ano", "Semana", "Data Inicial", "Fábrica"])
                  .sum()
                  .drop(columns="Turno")
                  .reset_index()
                  )

    # Garantir que a data seja datetime
    production["Data Inicial"] = pd.to_datetime(production["Data Inicial"])
    massa_week["Data Inicial"] = pd.to_datetime(massa_week["Data Inicial"])

    # Unir as duas tabelas
    df_analysis = pd.merge(production, massa_week, on=["Ano", "Semana", "Data Inicial", "Fábrica"], how="outer")

    # Criar uma coluna com a diferença entre massa produzida e consumida
    df_analysis["Dif. Baguete"] = df_analysis["Baguete Total(un)"] - df_analysis["Baguete"]
    df_analysis["Dif. Bolinha"] = df_analysis["Bolinha Total(un)"] - df_analysis["Bolinha"]

    # Reordenar as colunas
    df_analysis = df_analysis[
        [
            "Ano",
            "Semana",
            "Data Inicial",
            "Fábrica",
            "Baguete Total(un)",
            "Baguete",
            "Dif. Baguete",
            "Bolinha Total(un)",
            "Bolinha",
            "Dif. Bolinha",
        ]
    ]

    # Renomear Colunas
    df_analysis.columns = [
        "Ano",
        "Semana",
        "Data Inicial",
        "Fábrica",
        "Baguete Produzida(un)",
        "Baguete Consumida(un)",
        "Baguete Diferença(un)",
        "Bolinha Produzida(un)",
        "Bolinha Consumida(un)",
        "Bolinha Diferença(un)",
    ]

    # Ordenar pela semana e fábrica
    df_analysis = df_analysis.sort_values(by=["Ano", "Semana", "Fábrica"], ascending=[False, False,True])

    # ───────────────────────────────────────────────────────────────────── Gráfico De Análise ── #
    now = get_date.get_today()
    df_analysis_chart = df_analysis.copy()
    df_analysis_chart = df_analysis_chart[df_analysis_chart["Data Inicial"] >= now - pd.DateOffset(months=3)]

    # Mudar algumas colunas para o tipo float
    df_analysis_chart["Baguete Diferença(un)"] = df_analysis_chart["Baguete Diferença(un)"].astype(float)
    df_analysis_chart["Bolinha Diferença(un)"] = df_analysis_chart["Bolinha Diferença(un)"].astype(float)

    # Encontrar a % de Perda
    df_analysis_chart.loc[:, "Baguete Diferença(un)"] = ((df_analysis_chart["Baguete Diferença(un)"] / df_analysis_chart["Baguete Produzida(un)"]) * 100).round(2)
    df_analysis_chart.loc[:, "Bolinha Diferença(un)"] = ((df_analysis_chart["Bolinha Diferença(un)"] / df_analysis_chart["Bolinha Produzida(un)"]) * 100).round(2)

    # Adicionar colunas de fábrica
    df_analysis_chart.loc[:, "Baguete Fábrica 1"] = np.where(df_analysis_chart["Fábrica"] == "Fab. 1", df_analysis_chart["Baguete Diferença(un)"], 0)
    df_analysis_chart.loc[:, "Baguete Fábrica 2"] = np.where(df_analysis_chart["Fábrica"] == "Fab. 2", df_analysis_chart["Baguete Diferença(un)"], 0)

    # Preencher valores nulos das novas colunas
    df_analysis_chart.loc[:, "Baguete Fábrica 1"] = df_analysis_chart["Baguete Fábrica 1"].fillna(0)
    df_analysis_chart.loc[:, "Baguete Fábrica 2"] = df_analysis_chart["Baguete Fábrica 2"].fillna(0)

    # Plotar o gráfico
    fig = px.bar(
        df_analysis_chart,
        x="Data Inicial",
        y=["Baguete Fábrica 1", "Baguete Fábrica 2", "Bolinha Diferença(un)"],
        barmode="group",
        labels={
            "Data Inicial": "Data de Início",
            "Baguete Fábrica 1": "Baguete Fábrica 1 (%)",
            "Baguete Fábrica 2": "Baguete Fábrica 2 (%)",
            "Bolinha Diferença(un)": "Diferença Bolinha (%)",
            "value": "Diferença (%)",
            "variable": "Tipo de Pão"
        },
        template="plotly_white",
        range_y=[-100, 100],
    )

    st.plotly_chart(fig, use_container_width=True)

    # ────────────────────────────────────────────────────────────────────── Tabela De Análise ── #
    # Ajustar a data para dia/mês
    df_analysis["Data Inicial"] = pd.to_datetime(df_analysis["Data Inicial"]).dt.strftime("%d/%m")

    # Ajuste de cor
    def color_highlight(val):
        color = "red" if val > 0 else "black"
        return f"color: {color};"


    # Formatação dos números para o Brasil
    df_analysis_styled = df_analysis.style.format(thousands=".", decimal=",", precision=2)

    # Ajustar a cor para vermelho caso seja positivo(perda)
    df_analysis_styled = df_analysis_styled.map(
        color_highlight, subset=pd.IndexSlice[:, ["Baguete Diferença(un)", "Bolinha Diferença(un)"]]
    )

    # Exibir o dataframe
    st.dataframe(df_analysis_styled, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────────── Massa Por Semana ── #
    with st.expander("Visualização de Massa Semanal"):
        # Massa por semana e fábrica
        df_massa_week_grouped = (
            df_massa_week
            .groupby(["Ano", "Semana", "Data Inicial", "Fábrica"])
            .sum()
            .drop(columns="Turno")
            .reset_index()
            )
        # Ordenar pela semana e fábrica
        df_massa_week_grouped = df_massa_week_grouped.sort_values(
            by=["Ano", "Semana", "Fábrica"], ascending=[False, False, True]
        )
        # Ajustar data para dia/mês
        df_massa_week_grouped["Data Inicial"] = (
            pd.to_datetime(df_massa_week_grouped["Data Inicial"]).dt.strftime("%d/%m")
        )
        # Formatação dos números para o Brasil
        df_massa_week_grouped = df_massa_week_grouped.style.format(thousands=".", decimal=",", precision=2)
        # Exibir o dataframe
        st.dataframe(df_massa_week_grouped, use_container_width=True, hide_index=True)

    # ────────────────────────────────────────────────────────────────────────── Massa Por Dia ── #
    with st.expander("Visualização de Massa Data/Fábrica"):
        # Massa por data e fábrica
        df_massa_total = df_massa.groupby(["Data", "Fábrica"]).sum().drop(columns="Turno").reset_index()
        # Ordenar por data e fábrica
        df_massa_total = df_massa_total.sort_values(by=["Data", "Fábrica"], ascending=[False, True])
        # Ajustar data para dia/mês
        df_massa_total["Data"] = pd.to_datetime(df_massa_total["Data"]).dt.strftime("%d/%m")
        # Formatação dos números para o Brasil
        df_massa_total = df_massa_total.style.format(thousands=".", decimal=",", precision=2)
        # Exibir o dataframe
        st.dataframe(df_massa_total, hide_index=True, use_container_width=True)

#    ╭─                                                                                    ─╮
#    │                               Visualização da produção                               │
#    ╰─                                                                                    ─╯

if pg_selection == PageSelection.PRODUCAO_PAES.value:
    st.subheader("Produção de Pães")
    # Ajusta a tabela de pão
    df_prod_pao = adjust_pao(df_caixas_cf)

    # Ajustar a data
    df_prod_pao["Data Inicial"] = pd.to_datetime(df_prod_pao["Data Inicial"]).dt.strftime("%d/%m")

    # Ordenar
    df_prod_pao = df_prod_pao.sort_values(by=["Ano", "Semana", "Fábrica"], ascending=[False, False, True])

    # Formatação dos números para o Brasil
    df_prod_pao = df_prod_pao.style.format(thousands=".", decimal=",", precision=2)

    # Exibir o dataframe
    st.dataframe(df_prod_pao, use_container_width=True, hide_index=True, height=500)