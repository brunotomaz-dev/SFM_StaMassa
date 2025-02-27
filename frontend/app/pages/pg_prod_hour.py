"""
Módulo responsável por renderizar a página de produção por hora.
"""

import asyncio
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

# pylint: disable=E0401
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl
from app.functions.get_date import GetDate

get_date = GetDate()


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       Requisição de api
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


async def get_all_data() -> pd.DataFrame:
    """
    Função assíncrona que obtém os dados de todas as máquinas.

    Retorna um DataFrame com todos os dados de todas as máquinas.
    """

    # Obtém a data de hoje
    today = get_date.get_today()
    # Ajusta a data para o formato correto
    today = today.strftime("%Y-%m-%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"{APIUrl.URL_MAQ_INFO.value}?start={yesterday}&end={today}"
    tasks = [fetch_api_data(url)]
    results = await asyncio.gather(*tasks)
    return results[0]


@st.fragment(run_every=60)
def get_prod_data() -> None:
    """
    Atualiza os dados de produção por hora de todas as linhas a cada 60 segundos.
    Os dados são armazenados na variável de estado 'maq_info_2_days'.
    """
    container_p = st.empty()
    container_p.progress(5, "Atualizando dados...")
    data = asyncio.run(get_all_data())
    container_p.progress(100)
    st.session_state["maq_info_2_days"] = data
    container_p.empty()


if "maq_info_2_days" not in st.session_state:
    get_prod_data()


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                            Sidebar
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

select_option = st.sidebar.selectbox("Data dos dados:", ["Hoje", "Ontem"])


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                           Dataframe
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def adjust_selected_date(date_: str) -> str:
    """
    Ajusta a data para o formato correto.
    """
    if date_ == "Hoje":
        return get_date.get_today().strftime("%Y-%m-%d")

    return (get_date.get_today() - timedelta(days=1)).strftime("%Y-%m-%d")


@st.fragment(run_every=30)
def update_table() -> None:
    """Atualiza a tabela com os dados de produção por hora.

    Essa função é chamada a cada 30 segundos.

    Ela recebe os dados de produção por dia e ajusta para a data
    selecionada pelo usuário na sidebar.

    Em seguida, ela ajusta a data_hora para o formato correto e
    remove a linha 0 (máquina em preventiva).

    Depois, ela cria uma coluna com a data e hora, ajusta a data_hora
    para o formato correto e define data e linha como índices.

    Em seguida, ela agrupa os dados por linha e resample por hora,
    calcula a diferença entre o primeiro e o último - produção e
    ciclos e ajusta a produção - se a diferença de produção e ciclos
    for maior de 25%, o total deve ser o total de ciclos, se não for,
    o total deve ser o total de produção.

    Por fim, ela mantém apenas as colunas necessárias, ajusta os valores
    mínimos de 0 para coluna total, divide o total por 10 que é o número
    de bandejas por caixa e garante que as colunas sejam do tipo inteiro
    e valor mínimo de 0.

    A tabela resultante é então exibida na página.
    """

    # Recebe os dados
    df_original = st.session_state.maq_info_2_days

    # Ajustar a data para comparação
    df_original.data_registro = pd.to_datetime(df_original.data_registro)
    df_original.data_registro = df_original.data_registro.dt.strftime("%Y-%m-%d")

    # Cria uma cópia para manipulação
    df = df_original.copy()
    df = df[df.data_registro == adjust_selected_date(select_option)]

    if df.empty:
        st.subheader("Sem dados")
        st.stop()

    # Ajusta a data
    df.data_registro = pd.to_datetime(df.data_registro).dt.date

    # Se houver, remove a linha 0 (máquina em preventiva)
    df = df[df.linha != 0]

    # Cria uma coluna com a data e hora
    df["data_hora"] = (
        df.data_registro.astype(str) + " " + df.hora_registro.astype(str).str.split(".").str[0]
    )

    # Ajusta a data_hora para o formato correto
    df.data_hora = pd.to_datetime(df.data_hora)

    # Preencher a linha com 2 caracteres
    df.linha = df.linha.astype(str).str.zfill(2)

    # Ajustar o conteúdo da coluna linha para 'Linha 1' etc.
    df.linha = df.linha.apply(lambda x: f"Linha {x}")

    # Definir data e linha como índices
    df = df.set_index(["data_hora", "linha"])

    # Agrupar os dados
    df = (
        df.groupby("linha")
        .resample("h", level="data_hora")
        .agg(
            {
                "contagem_total_produzido": ["first", "last"],
                "contagem_total_ciclos": ["first", "last"],
            }
        )
    )

    # Calcular a diferença entre o primeiro e o último - produção
    df["total_produzido"] = (
        df["contagem_total_produzido"]["last"] - df["contagem_total_produzido"]["first"]
    )

    # Calcular a diferença entre o primeiro e o último - ciclos
    df["total_ciclos"] = df["contagem_total_ciclos"]["last"] - df["contagem_total_ciclos"]["first"]

    # Reiniciar o index
    df = df.reset_index()

    # Ajuste a produção - se a diferença de produção e ciclos for maior de 25%,
    # o total deve ser o total de ciclos, se não for, o total deve ser o total de produção
    mask = (df.total_ciclos - df.total_produzido) / df.total_ciclos > 0.25
    df["total"] = np.where(mask, df.total_ciclos, df.total_produzido)

    # Manter apenas as colunas necessárias
    df = df[["data_hora", "total", "linha"]]

    # Valores mínimos de 0 para coluna total
    df.loc[:, "total"] = df.total.fillna(0)

    # Dividir o total por 10 que é o número de bandejas por caixa
    df.loc[:, "total"] = np.floor(df.total / 10).astype(int)

    # Tabela para pivot
    df = df.pivot(index="data_hora", columns="linha", values="total")

    # Garantir que as colunas sejam do tipo inteiro e valor mínimo de 0
    df = df.fillna(0)
    df = df.astype(int)
    df = df.where(df > 0, 0)

    # Criar uma coluna com o intervalo de tempo
    df["Intervalo"] = df.index.hour.astype(str) + "hs - " + (df.index.hour + 1).astype(str) + "hs"

    # Fazer com que intervalo seja o index
    df = df.set_index("Intervalo")

    # Calcular o total de cada coluna (linha de produção)
    totals = df.sum(axis=0).to_frame().T

    # Adicionar uma nova linha com os totais ao DataFrame
    totals.index = ["Total"]
    df = pd.concat([df, totals])

    container.table(df)


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃                                        Layout                                        ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

st.subheader("Caixas Produzidas por Hora")
container = st.empty()
update_table()
get_prod_data()
