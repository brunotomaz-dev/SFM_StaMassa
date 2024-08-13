"""
Módulo principal da aplicação. Define as rotas da API.
CreatedAT: 09/08/2024
CreatedBy: Bruno Tomaz
"""

from datetime import datetime, timedelta

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

# pylint: disable=E0401
from src.controller.efficiency_controller import EfficiencyController
from src.controller.info_ihm_controller import InfoIHMController
from src.controller.maquina_ihm_controller import MaquinaIHMController
from src.controller.maquina_info_controller import MaquinaInfoController
from src.controller.maquina_qualidade_controller import MaquinaQualidadeController
from src.controller.performance_controller import PerformanceController
from src.controller.production_controller import ProductionController
from src.controller.reparo_controller import ReparoController
from src.functions import date_f
from src.helpers.variables import IndicatorType
from src.service.functions.ind_prod import IndProd
from src.service.functions.info_ihm_join import InfoIHMJoin
from src.service.functions.prod_qualid_join import ProdQualidJoin

app = FastAPI()

maquina_ihm_controller = MaquinaIHMController()
maquina_info_controller = MaquinaInfoController()
maquina_qualidade_controller = MaquinaQualidadeController()
production_controller = ProductionController()
info_ihm_controller = InfoIHMController()
prod_qualid_join = ProdQualidJoin()
eff_controller = EfficiencyController()
perf_controller = PerformanceController()
reparo_controller = ReparoController()
ind_production = IndProd()

pd.set_option("future.no_silent_downcast", True)


# ================================================================================================ #
#                                               ROTAS                                              #
# ================================================================================================ #
@app.get("/")
def read_root():
    """Rota principal da API."""
    return {"Hello": "World"}


# ========================================= Automação DB ========================================= #
@app.get("/maquina_ihm")
def get_maquina_ihm(start: str, end: str):
    """
    Retorna os dados da máquina IHM no intervalo de datas especificado.
    Parâmetros:
    - start (str): Data de início do intervalo no formato 'YYYY-MM-DD'.
    - end (str): Data de término do intervalo no formato 'YYYY-MM-DD'.
    Retorna:
    - JSONResponse: Resposta JSON contendo os dados da máquina IHM no formato ISO.
    Exemplo:
    >>> get_maquina_ihm('2022-01-01', '2022-01-31')
    {
        "data": [
            {
                "timestamp": "2022-01-01T00:00:00",
                "valor1": 10,
                "valor2": 20
            },
            {
                "timestamp": "2022-01-02T00:00:00",
                "valor1": 15,
                "valor2": 25
            },
            ...
        ]
    }
    """

    data = maquina_ihm_controller.get_data((start, end))
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


@app.get("/maquina_info/")
def get_maquina_info(start: str, end: str):
    """
    Retorna os dados da máquina info no intervalo de datas especificado.
    Parâmetros:
    - start (str): Data de início do intervalo no formato 'YYYY-MM-DD'.
    - end (str): Data de término do intervalo no formato 'YYYY-MM-DD'.
    Retorna:
    - JSONResponse: Resposta JSON contendo os dados da máquina Infono formato ISO.
    Exemplo:
    >>> get_maquina_ihm('2022-01-01', '2022-01-31')
    {
        "data": [
            {
                "timestamp": "2022-01-01T00:00:00",
                "valor1": 10,
                "valor2": 20
            },
            {
                "timestamp": "2022-01-02T00:00:00",
                "valor1": 15,
                "valor2": 25
            },
            ...
        ]
    }
    """

    data = maquina_info_controller.get_data((start, end))
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


@app.get("/maquina_qualidade")
def get_maquina_qualidade(start: str, end: str):
    """
    Retorna os dados da máquina qualidade no intervalo de datas especificado.
    Parâmetros:
    - start (str): Data de início do intervalo no formato 'YYYY-MM-DD'.
    - end (str): Data de término do intervalo no formato 'YYYY-MM-DD'.
    Retorna:
    - JSONResponse: Resposta JSON contendo os dados da máquina IHM no formato ISO.
    Exemplo:
    >>> get_maquina_ihm('2022-01-01', '2022-01-31')
    {
        "data": [
            {
                "timestamp": "2022-01-01T00:00:00",
                "valor1": 10,
                "valor2": 20
            },
            {
                "timestamp": "2022-01-02T00:00:00",
                "valor1": 15,
                "valor2": 25
            },
            ...
        ]
    }
    """

    data = maquina_qualidade_controller.get_data((start, end))
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


@app.get("/production")
def get_production():
    """
    Retorna os dados de produção do DB local do mês corrente.
    Retorna:
    - JSONResponse: Resposta JSON contendo os dados da produção no formato ISO.
    """

    data = production_controller.get_data()
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


@app.get("/info_ihm")
def get_info_ihm():
    """
    Retorna os dados de info_ihm do DB local do mês corrente.
    Retorna:
    - JSONResponse: Resposta JSON contendo os dados da produção no formato ISO.
    """

    data = info_ihm_controller.get_data()
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


@app.get("/efficiency")
def get_efficiency():
    """
    Retorna os indicadores de eficiência do DB local do mês corrente.
    Retorna:
    - JSONResponse: Resposta JSON contendo os indicadores de eficiência no formato ISO.
    """

    data = eff_controller.get_data()
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


@app.get("/performance")
def get_performance():
    """
    Retorna os indicadores de performance do DB local do mês corrente.
    Retorna:
    - JSONResponse: Resposta JSON contendo os indicadores de performance no formato ISO.
    """

    data = perf_controller.get_data()
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


@app.get("/reparo")
def get_reparo():
    """
    Retorna os indicadores de reparo do DB local do mês corrente.
    Retorna:
    - JSONResponse: Resposta JSON contendo os indicadores de reparo no formato ISO.
    """

    data = reparo_controller.get_data()
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")


# ================================================================================================ #
#                                           LOCAL DB JOBS                                          #
# ================================================================================================ #


# Função para criar o dataframe de produção do mês corrente
def create_production_data():
    """Cria os dados de produção do mês corrente e salva no banco de dados local."""

    # Obter as datas do mês corrente
    start, end = date_f.get_first_and_last_day_of_month()
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")

    # Obter os dados da máquina Info e Qualidade
    prod = maquina_info_controller.get_production_data((start, end))
    qual = maquina_qualidade_controller.get_data((start, end))

    # Juntar os dados de produção com os dados de qualidade e info
    data = prod_qualid_join.join_data(qual, prod)

    # Salva no banco de dados local
    production_controller.replace_data(data)


# Função para criar dataframe com os dados de maquina IHM e info, e salvar no banco de dados local
def create_maq_ihm_info_data():
    """Cria os dados de maquina IHM e Info e salva no banco de dados local."""

    # Obter as datas do mês corrente
    start, end = date_f.get_first_and_last_day_of_month()
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")

    # Obter os dados da máquina Info e Qualidade
    maq_ihm = maquina_ihm_controller.get_data((start, end))
    maq_info = maquina_info_controller.get_data((start, end))

    info_ihm_join = InfoIHMJoin(maq_ihm, maq_info)

    # Unir os dados de maquina IHM e info
    data = info_ihm_join.join_data()

    # Salva no banco de dados local
    info_ihm_controller.replace_data(data)


# Função para criar indicadores de produção
def create_ind_prod():
    """Cria os indicadores de produção do mês corrente e salva no banco de dados local."""

    # Obter os dados locais de produção
    df_production = production_controller.get_data()

    # Obter os dados locais de maquina IHM e Info
    df_info_ihm = info_ihm_controller.get_data()

    # Criar os indicadores de produção
    df_eff = ind_production.get_indicators(df_info_ihm, df_production, IndicatorType.EFFICIENCY)
    df_perf = ind_production.get_indicators(df_info_ihm, df_production, IndicatorType.PERFORMANCE)
    df_repair = ind_production.get_indicators(df_info_ihm, df_production, IndicatorType.REPAIR)

    # Salvar os indicadores no banco de dados local
    eff_controller.replace_data(df_eff)
    perf_controller.replace_data(df_perf)
    reparo_controller.replace_data(df_repair)


# ================================================================================================ #
#                                      AGENDAMENTO DE TAREFAS                                      #
# ================================================================================================ #

# Inicializa o agendador de tarefas
scheduler = BackgroundScheduler()

# Cria a tarefa de criação dos dados de produção do mês corrente
scheduler.add_job(
    create_production_data,
    "interval",
    minutes=5,
    start_date=datetime.now() + timedelta(seconds=5),
)

# Cria a tarefa para criar os dados de maquina IHM e Info do mês corrente
scheduler.add_job(
    create_maq_ihm_info_data,
    "interval",
    minutes=5,
    start_date=datetime.now() + timedelta(seconds=3),
)

# Cria a tarefa para criar os indicadores de produção
scheduler.add_job(
    create_ind_prod,
    "interval",
    minutes=2,
    start_date=datetime.now() + timedelta(seconds=1),
)

# Inicia o agendador
scheduler.start()
