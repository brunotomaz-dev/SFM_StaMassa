import asyncio
import time
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
from app.helpers.variables import RENDIMENTO_PASTA_PAO

get_date = GetDate()


class PageSelection(Enum):
    MASSA = "Massa"
    PASTA = "Pasta"
    PRODUCAO_PAES = "Produção de Pães"
    AJUSTE_ESTOQUE = "Ajuste de Estoque"


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

@st.cache_data(show_spinner="Obtendo dados", ttl=60000)
def get_estoque(start_date:str, end_date:str):

    return asyncio.run(get_data(APIUrl.URL_PCP_ESTOQUE.value, start_date, end_date))



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
            stc.MenuItem(PageSelection.AJUSTE_ESTOQUE.value, icon="bi bi-boxes"),
        ]
    )

if pg_selection == PageSelection.AJUSTE_ESTOQUE.value:
    # Primeiro e último dia do mês
    start_day, end_day = get_date.get_this_month()

    # Usar start e retroceder 6 meses
    start_day = start_day - pd.DateOffset(months=6)

    date_choice = st.sidebar.date_input(label="Escolha a data inicial e final", value=(start_day, end_day), format="DD/MM/YYYY")

    first, last = date_choice

    first = str(first).replace("-", "")
    last = str(last).replace("-", "")

    df_estoque = get_estoque(first, last)



#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframes
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

df_massa, df_pasta, df_massa_week, df_pasta_week, df_caixas_cf = get_df()

if pg_selection == PageSelection.AJUSTE_ESTOQUE.value:
    # Ajustar a data para datetime
    df_estoque["data_emissao"] = pd.to_datetime(df_estoque["data_emissao"], format="%Y%m%d")

    # Ordenar pela data de emissão
    df_estoque = df_estoque.sort_values(by="data_emissao", ascending=False)

    # Ajustar a data para dia/mês/ano
    df_estoque["data_emissao"] = df_estoque["data_emissao"].dt.strftime("%d/%m/%Y")

    # Filtra coluna filial para ter apenas as filias 101 e 201
    df_estoque = df_estoque[df_estoque["filial"].isin([101, 201])]

    # Na coluna codigo_fornecedor, substituir DE0 por Devolução e RE0 por Remessa
    df_estoque["tipo"] = df_estoque["tipo"].replace(
        {"DE0": "Devolução", "RE0": "Remessa"}
    )



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
df_massa.columns = ["Data", *massa_columns]

df_massa_week.columns = [
    "Ano",
    "Semana",
    "Data Inicial",
    *massa_columns,
]

# Ajustar o formato da coluna "Data"
df_massa["Data"] = pd.to_datetime(df_massa["Data"]).dt.date
df_massa_week["Data Inicial"] = pd.to_datetime(df_massa_week["Data Inicial"]).dt.date

pasta_columns = [
    "Turno",
    "Fábrica",
    "Tradicional Batidas",
    "Tradicional Peso",
    "Picante Batidas",
    "Picante Peso",
    "Cebola Batidas",
    "Cebola Peso",
    "Doce Batidas",
    "Doce Peso",
]

df_pasta.columns = ["Data", *pasta_columns]

df_pasta_week.columns = [
    "Ano",
    "Semana",
    "Data Inicial",
    *pasta_columns,
]

# Ajustar o formato da coluna "Data"
df_pasta["Data"] = pd.to_datetime(df_pasta["Data"]).dt.date
df_pasta_week["Data Inicial"] = pd.to_datetime(df_pasta_week["Data Inicial"]).dt.date

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                             Layout
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
st.header("PCP")

#    ╭─                                                                                    ─╮
#    │                                Visualização de Massa                                 │
#    ╰─                                                                                    ─╯

# Ajustar a produção de pães
production = adjust_pao(df_caixas_cf)

if pg_selection == PageSelection.MASSA.value:
    st.subheader("Análise de Massa - Produzido x Consumido")

    # ─────────────────────────────────────────────────────────────────────── Análise De Massa ── #
    df_production = production.copy()

    # Máscara para selecionar pão bolinha
    mask = df_production["Produto"].str.contains("BOL ")

    # Adicionar a produção de Bolinha a uma coluna
    df_production["Bolinha"] = mask.astype(int) * df_production["Pães"]
    # Remover a produção de bolinha da coluna de pão
    df_production["Baguete"] = df_production["Pães"].sub(df_production["Bolinha"])

    # Agrupar por ano, semana e fábrica
    df_production = (df_production
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
    df_production["Data Inicial"] = pd.to_datetime(df_production["Data Inicial"])
    massa_week["Data Inicial"] = pd.to_datetime(massa_week["Data Inicial"])

    # Unir as duas tabelas
    df_analysis = pd.merge(df_production, massa_week, on=["Ano", "Semana", "Data Inicial", "Fábrica"], how="outer")

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
    df_analysis = df_analysis.sort_values(by=["Ano", "Semana", "Fábrica"], ascending=[False, False, True])

    # ───────────────────────────────────────────────────────────────────── Gráfico De Análise ── #
    now = get_date.get_today()
    df_analysis_chart = df_analysis.copy()
    df_analysis_chart = df_analysis_chart[df_analysis_chart["Data Inicial"] >= now - pd.DateOffset(months=3)]

    # Mudar algumas colunas para o tipo float
    df_analysis_chart["Baguete Diferença(un)"] = df_analysis_chart["Baguete Diferença(un)"].astype(float)
    df_analysis_chart["Bolinha Diferença(un)"] = df_analysis_chart["Bolinha Diferença(un)"].astype(float)

    # Encontrar a % de Perda
    df_analysis_chart.loc[:, "Baguete Diferença(un)"] = (
                (df_analysis_chart["Baguete Diferença(un)"] / df_analysis_chart["Baguete Produzida(un)"]) * 100).round(
        2)
    df_analysis_chart.loc[:, "Bolinha Diferença(un)"] = (
                (df_analysis_chart["Bolinha Diferença(un)"] / df_analysis_chart["Bolinha Produzida(un)"]) * 100).round(
        2)

    # Adicionar colunas de fábrica
    df_analysis_chart.loc[:, "Baguete Fábrica 1"] = np.where(df_analysis_chart["Fábrica"] == "Fab. 1",
                                                             df_analysis_chart["Baguete Diferença(un)"], 0)
    df_analysis_chart.loc[:, "Baguete Fábrica 2"] = np.where(df_analysis_chart["Fábrica"] == "Fab. 2",
                                                             df_analysis_chart["Baguete Diferença(un)"], 0)

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
#    │                                Visualização de pasta                                 │
#    ╰─                                                                                    ─╯

if pg_selection == PageSelection.PASTA.value:
    st.subheader("Análise de Pasta - Produzido x Consumido")

    # ────────────────────────────────────────────────────────────────────── Análise De Pasta ── #
    # Ajustar a produção de pães
    df_prod = production.copy()

    # Calcular a quantidade de pasta usada por produto
    df_prod["Pasta usada(kg)"] = df_prod["Pães"] * df_prod["Produto"].map(RENDIMENTO_PASTA_PAO)

    # Mapeamento de produto
    prod_dict = {
        r".*TRD.*": "Tradicional",
        r".*CEB.*": "Cebola",
        r".*PIC.*": "Picante",
        r".*DOCE.*": "Doce",
    }

    # Substituir o nome do produto
    df_prod["Produto"] = df_prod["Produto"].replace(prod_dict, regex=True)

    # Agrupar por ano, semana e fábrica
    df_prod = (df_prod
               .groupby(["Ano", "Semana", "Data Inicial", "Fábrica", "Produto"])
               .sum()
               .reset_index()
               )

    # Pivot table
    df_prod = df_prod.pivot_table(
        index=["Ano", "Semana", "Data Inicial", "Fábrica"],
        columns="Produto",
        values="Pasta usada(kg)",
        fill_value=0,
    ).reset_index()

    # Pasta por semana
    df_pasta_w = df_pasta_week.copy()

    # Agrupar por ano, semana e fábrica
    df_pasta_w = (df_pasta_w.groupby(["Ano", "Semana", "Data Inicial", "Fábrica"])
                  .sum()
                  .drop(columns="Turno")
                  .reset_index()
                  )

    # Garantir que as datas das tabelas sejam datetime
    df_prod["Data Inicial"] = pd.to_datetime(df_prod["Data Inicial"]).dt.date
    df_pasta_w["Data Inicial"] = pd.to_datetime(df_pasta_w["Data Inicial"]).dt.date

    # Unir as duas tabelas
    df_pasta_w = pd.merge(df_pasta_w, df_prod, on=["Ano", "Semana", "Data Inicial", "Fábrica"], how="outer")

    # Timer para garantir união das tabelas
    time.sleep(1)

    # Calcular a diferença entre a pasta produzida e consumida
    for col in df_pasta_w.columns[12:]:
        df_pasta_w[f"{col} Diferença(kg)"] = df_pasta_w[f"{col} Peso"] - df_pasta_w[col]

    # Ordenar por data
    df_pasta_w = df_pasta_w.sort_values(by=["Ano", "Semana", "Fábrica"], ascending=[False, False, True])

    # Ordenar as colunas para melhor visualização
    df_pasta_w = df_pasta_w[
        [
            "Ano",
            "Semana",
            "Data Inicial",
            "Fábrica",
            "Tradicional Peso",
            "Tradicional",
            "Tradicional Diferença(kg)",
            "Picante Peso",
            "Picante",
            "Picante Diferença(kg)",
            "Cebola Peso",
            "Cebola",
            "Cebola Diferença(kg)",
            "Doce Peso",
            "Doce",
            "Doce Diferença(kg)",
        ]
    ]

    # Renomear colunas
    df_pasta_w = df_pasta_w.rename(columns={
        "Tradicional": "Tradicional Consumido(kg)",
        "Picante": "Picante Consumido(kg)",
        "Cebola": "Cebola Consumido(kg)",
        "Doce": "Doce Consumido(kg)",
        "Tradicional Peso": "Tradicional Produzido(kg)",
        "Picante Peso": "Picante Produzido(kg)",
        "Cebola Peso": "Cebola Produzido(kg)",
        "Doce Peso": "Doce Produzido(kg)",
    })

    # ────────────────────────────────────────────────────────────────────────── Análise Chart ── #
    df_pasta_chart = df_pasta_w.copy()

    # Encontrar a % de Perda
    df_pasta_chart["Tradicional Diferença(kg)"] = ((df_pasta_chart["Tradicional Diferença(kg)"] / df_pasta_chart[
        "Tradicional Produzido(kg)"]) * 100).round(2)
    df_pasta_chart["Picante Diferença(kg)"] = (
                (df_pasta_chart["Picante Diferença(kg)"] / df_pasta_chart["Picante Produzido(kg)"]) * 100).round(2)
    df_pasta_chart["Cebola Diferença(kg)"] = (
                (df_pasta_chart["Cebola Diferença(kg)"] / df_pasta_chart["Cebola Produzido(kg)"]) * 100).round(2)
    df_pasta_chart["Doce Diferença(kg)"] = (
                (df_pasta_chart["Doce Diferença(kg)"] / df_pasta_chart["Doce Produzido(kg)"]) * 100).round(2)

    # Ajustar período
    now = get_date.get_today()
    # Voltar 3 meses e manter a data
    mask = (now - pd.DateOffset(months=3)).date()
    # Filtrar pela data
    df_pasta_chart = df_pasta_chart[df_pasta_chart["Data Inicial"] >= mask]

    # Chart
    fig = px.bar(
        df_pasta_chart,
        x="Data Inicial",
        y=["Tradicional Diferença(kg)", "Picante Diferença(kg)", "Cebola Diferença(kg)", "Doce Diferença(kg)"],
        barmode="group",
        custom_data=["Fábrica"],
        labels={
            "Data Inicial": "Data de Início",
            "value": "Diferença (%)",
            "variable": "Tipo de Pasta",
        },
        template="plotly_white",
        range_y=[-100, 100],
    )

    fig.update_traces(
        hovertemplate="<br>".join([
            "Data de Início: %{x}",
            "Diferença (%): %{y}",
            "Fábrica: %{customdata[0]}"
        ])
    )

    st.plotly_chart(fig, use_container_width=True)

    # ────────────────────────────────────────────────────────────────────────── Análise Table ── #
    # Ajustar a data para dia/mês
    df_pasta_w["Data Inicial"] = pd.to_datetime(df_pasta_w["Data Inicial"]).dt.strftime("%d/%m")


    # Ajuste de cor
    def color_highlight(val):
        color = "red" if val > 0 else "black"
        return f"color: {color};"


    # Formatar números para o Brasil
    df_pasta_w = df_pasta_w.style.format(thousands=".", decimal=",", precision=2)

    # Ajustar a cor para vermelho caso seja positivo(perda)
    df_pasta_w = df_pasta_w.map(
        color_highlight, subset=pd.IndexSlice[:, [
                                                     "Tradicional Diferença(kg)",
                                                     "Picante Diferença(kg)",
                                                     "Cebola Diferença(kg)",
                                                     "Doce Diferença(kg)",
                                                 ]]
    )
    # Exibir o dataframe
    st.dataframe(df_pasta_w, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────────── Pasta Por Semana ── #
    with st.expander("Visualização de Pasta Semanal"):
        # Pasta por semana e fábrica
        df_pasta_week_grouped = (
            df_pasta_week
            .groupby(["Ano", "Semana", "Data Inicial", "Fábrica"])
            .sum()
            .drop(columns="Turno")
            .reset_index()
        )
        # Ordenar pela semana e fábrica
        df_pasta_week_grouped = df_pasta_week_grouped.sort_values(
            by=["Ano", "Semana", "Fábrica"], ascending=[False, False, True]
        )
        # Ajustar data para dia/mês
        df_pasta_week_grouped["Data Inicial"] = (
            pd.to_datetime(df_pasta_week_grouped["Data Inicial"]).dt.strftime("%d/%m")
        )
        # Formatação dos números para o Brasil
        df_pasta_week_grouped = df_pasta_week_grouped.style.format(thousands=".", decimal=",", precision=2)
        # Exibir o dataframe
        st.dataframe(df_pasta_week_grouped, use_container_width=True, hide_index=True)

    # ────────────────────────────────────────────────────────────────────────── Pasta Por Dia ── #
    with st.expander("Visualização de Pasta Data/Fábrica"):
        # Pasta por data e fábrica
        df_pasta_total = df_pasta.groupby(["Data", "Fábrica"]).sum().drop(columns="Turno").reset_index()
        # Ordenar por data e fábrica
        df_pasta_total = df_pasta_total.sort_values(by=["Data", "Fábrica"], ascending=[False, True])
        # Ajustar data para dia/mês
        df_pasta_total["Data"] = pd.to_datetime(df_pasta_total["Data"]).dt.strftime("%d/%m")
        # Formato dos números para o Brasil
        df_pasta_total = df_pasta_total.style.format(thousands=".", decimal=",", precision=2)
        # Exibir o dataframe
        st.dataframe(df_pasta_total, hide_index=True, use_container_width=True)

#    ╭─                                                                                    ─╮
#    │                               Visualização da produção                               │
#    ╰─                                                                                    ─╯

if pg_selection == PageSelection.PRODUCAO_PAES.value:
    st.subheader("Produção de Pães")
    # Ajusta a tabela de pão
    df_prod_pao = production.copy()

    # Ajustar a data
    df_prod_pao["Data Inicial"] = pd.to_datetime(df_prod_pao["Data Inicial"]).dt.strftime("%d/%m")

    # Ordenar
    df_prod_pao = df_prod_pao.sort_values(by=["Ano", "Semana", "Fábrica"], ascending=[False, False, True])

    # Formatação dos números para o Brasil
    df_prod_pao = df_prod_pao.style.format(thousands=".", decimal=",", precision=2)

    # Exibir o dataframe
    st.dataframe(df_prod_pao, use_container_width=True, hide_index=True, height=500)

#    ╭─                                                                                    ─╮
#    │                          Visualização do ajuste de estoque                           │
#    ╰─                                                                                    ─╯

if pg_selection == PageSelection.AJUSTE_ESTOQUE.value:
    st.subheader("Ajuste de Estoque")

    st.dataframe(df_estoque, use_container_width=True, hide_index=True)
