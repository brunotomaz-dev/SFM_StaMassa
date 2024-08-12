"""
Módulo principal da aplicação. Define as rotas da API.
CreatedAT: 09/08/2024
CreatedBy: Bruno Tomaz
"""

from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

# pylint: disable=E0401
from src.controller.maquina_ihm_controller import MaquinaIHMController
from src.controller.maquina_info_controller import MaquinaInfoController
from src.controller.maquina_qualidade_controller import MaquinaQualidadeController
from src.controller.production_controller import ProductionController
from src.functions import date_f
from src.service.functions.prod_qualid_join import ProdQualidJoin

app = FastAPI()

maquina_ihm_controller = MaquinaIHMController()
maquina_info_controller = MaquinaInfoController()
maquina_qualidade_controller = MaquinaQualidadeController()
production_controller = ProductionController()
prod_qualid_join = ProdQualidJoin()


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


@app.get("/maquina_info/production")
def get_maquina_info_production():
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


# ================================================================================================ #
#                                           LOCAL DB JOBS                                          #
# ================================================================================================ #


# Função para criar o dataframe de produção do mês corrente
def create_production_data():

    # Obter as datas do mês corrente
    start, end = date_f.get_first_and_last_day_of_month()
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")

    # Obter os dados da máquina Info e Qualidade
    prod = maquina_info_controller.get_data((start, end))
    qual = maquina_qualidade_controller.get_data((start, end))

    # Juntar os dados de produção com os dados de qualidade e info
    data = prod_qualid_join.join_data(qual, prod)

    # Salva no banco de dados local
    production_controller.replace_data(data)


# ================================================================================================ #
#                                      AGENDAMENTO DE TAREFAS                                      #
# ================================================================================================ #

# Inicializa o agendador de tarefas
scheduler = BackgroundScheduler()

# Cria a tarefa de criação dos dados de produção do mês corrente
scheduler.add_job(
    create_production_data,
    "interval",
    minutes=10,
    start_date=datetime.now() + timedelta(seconds=5),
)

# Inicia o agendador
scheduler.start()
