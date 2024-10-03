"""
Módulo principal da aplicação. Define as rotas da API.
CreatedAT: 09/08/2024
CreatedBy: Bruno Tomaz
"""

import logging
from datetime import datetime, timedelta

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse

# pylint: disable=E0401
from src.controller.efficiency_controller import EfficiencyController
from src.controller.historic_ind_controller import HistoricIndController
from src.controller.info_ihm_controller import InfoIHMController
from src.controller.maquina_ihm_controller import MaquinaIHMController
from src.controller.maquina_info_controller import MaquinaInfoController
from src.controller.maquina_qualidade_controller import MaquinaQualidadeController
from src.controller.performance_controller import PerformanceController
from src.controller.production_controller import ProductionController
from src.controller.protheus_cyv_controller import ProtheusCYVController
from src.controller.protheus_sb1_produtos_controller import ProtheusSB1ProdutosController
from src.controller.protheus_sb2_estoque_controller import ProtheusSB2EstoqueController
from src.controller.protheus_sd3_pcp_controller import ProtheusSD3PCPController
from src.controller.protheus_sd3_production_controller import ProtheusSD3ProductionController
from src.controller.reparo_controller import ReparoController
from src.functions import date_f
from src.functions import history_functions as hist_f
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
historic_ind_controller = HistoricIndController()
ind_production = IndProd()
protheus_sb1_produtos_controller = ProtheusSB1ProdutosController()
protheus_cyv_controller = ProtheusCYVController()
protheus_sd3_production_controller = ProtheusSD3ProductionController()
protheus_sd3_pcp_controller = ProtheusSD3PCPController()
protheus_sb2_caixas_estoque_controller = ProtheusSB2EstoqueController()

# Remover os warnings de downcast do pandas
pd.set_option("future.no_silent_downcast", True)

# Configura o logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def create_json_response(data: pd.DataFrame) -> JSONResponse:
    """Cria uma resposta JSON a partir de um DataFrame do pandas."""
    if data is None or data.empty:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return JSONResponse(content=data.to_json(date_format="iso", orient="split"))


# ================================================================================================ #
#                                               ROTAS                                              #
# ================================================================================================ #
@app.get("/")
def read_root():
    """Rota principal da API."""
    return {"Hello": "World"}


# ========================================= Automação DB ========================================= #
@app.get("/maquina_ihm")
def get_maquina_ihm(start: str, end: str) -> JSONResponse:
    """
    Retorna os dados da máquina IHM no intervalo de datas especificado.
    """
    try:
        data = maquina_ihm_controller.get_data((start, end))
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/maquina_info/")
def get_maquina_info(start: str, end: str) -> JSONResponse:
    """
    Retorna os dados da máquina info no intervalo de datas especificado.
    """
    try:
        data = maquina_info_controller.get_data((start, end))
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/maquina_qualidade")
def get_maquina_qualidade(start: str, end: str) -> JSONResponse:
    """
    Retorna os dados da máquina qualidade no intervalo de datas especificado.
    """
    try:
        data = maquina_qualidade_controller.get_data((start, end))
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/production")
def get_production() -> JSONResponse:
    """
    Retorna os dados de produção do DB local do mês corrente.
    """
    try:
        data = production_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/info_ihm")
def get_info_ihm() -> JSONResponse:
    """
    Retorna os dados de info_ihm do DB local do mês corrente.
    """
    try:
        data = info_ihm_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/efficiency")
def get_efficiency() -> JSONResponse:
    """
    Retorna os indicadores de eficiência do DB local do mês corrente.
    """
    try:
        data = eff_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/performance")
def get_performance() -> JSONResponse:
    """
    Retorna os indicadores de performance do DB local do mês corrente.
    """
    try:
        data = perf_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/reparo")
def get_reparo() -> JSONResponse:
    """
    Retorna os indicadores de reparo do DB local do mês corrente.
    """
    try:
        data = reparo_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/historic_ind")
def get_historic_ind() -> JSONResponse:
    """
    Retorna os dados de histórico de indicadores do DB local.
    """
    try:
        data = historic_ind_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ═══════════════════════════════════════════════════════════════════════════════════ Protheus ══ #
@app.get("/protheus_sb1")
def get_protheus_sb1() -> JSONResponse:
    """
    Retorna os dados de SB1 do DB local.
    """
    try:
        data = protheus_sb1_produtos_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/protheus_cyv/massa")
def get_protheus_cyv_massa() -> JSONResponse:
    """
    Retorna os dados de CYV Massa do DB local.
    """
    try:
        data = protheus_cyv_controller.get_massa_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/protheus_cyv/massa_week")
def get_protheus_cyv_massa_week() -> JSONResponse:
    """
    Retorna os dados de CYV Massa do DB local.
    """
    try:
        data = protheus_cyv_controller.get_massa_week_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/protheus_cyv/pasta")
def get_protheus_cyv_pasta() -> JSONResponse:
    """
    Retorna os dados de CYV Pasta do DB local.
    """
    try:
        data = protheus_cyv_controller.get_pasta_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/protheus_cyv/pasta_week")
def get_protheus_cyv_pasta_week() -> JSONResponse:
    """
    Retorna os dados de CYV Pasta do DB local.
    """
    try:
        data = protheus_cyv_controller.get_pasta_week_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/protheus_sd3/production")
def get_protheus_sd3_production(week: bool = Query(False)) -> JSONResponse:
    """
    Retorna os dados de SD3 Produção do DB local.
    """
    try:
        data = protheus_sd3_production_controller.get_sd3_data(week)
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/protheus_sd3/pcp_estoque")
def get_protheus_sd3_ajuste_estoque(start: str, end: str) -> JSONResponse:
    """
    Retorna os dados de SD3 Ajuste de Estoque do DB local.
    """
    try:
        data = protheus_sd3_pcp_controller.get_sd3_data(start, end)
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/protheus_sb2/caixas_estoque")
def get_protheus_sb2_caixas_estoque() -> JSONResponse:
    """
    Retorna os dados de SB2 Caixas Estoque do DB local.
    """
    try:
        data = protheus_sb2_caixas_estoque_controller.get_data()
        return create_json_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================================================================================ #
#                                           LOCAL DB JOBS                                          #
# ================================================================================================ #


# Função para criar o dataframe de produção do mês corrente
def create_production_data() -> None:
    """Cria os dados de produção do mês corrente e salva no banco de dados local."""

    try:
        # Obter as datas do mês corrente
        start, end = date_f.get_first_and_last_day_of_month()
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")

        # Obter os dados da máquina Info e Qualidade
        prod = maquina_info_controller.get_production_data((start, end))
        qual = maquina_qualidade_controller.get_data((start, end))

        # Receber os produtos do protheus
        products_data = protheus_sb1_produtos_controller.get_data()

        # Juntar os dados de produção com os dados de qualidade e info
        data = prod_qualid_join.join_data(qual, prod, products_data)

        # Salva no banco de dados local
        production_controller.replace_data(data)
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar dados de produção: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar dados de produção: %s", e, exc_info=True)


# Função para criar dataframe com os dados de maquina IHM e info, e salvar no banco de dados local
def create_maq_ihm_info_data() -> None:
    """Cria os dados de maquina IHM e Info e salva no banco de dados local."""

    try:
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
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar dados de maquina IHM e Info: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar dados de maquina IHM e Info: %s", e, exc_info=True)


# Função para criar indicadores de produção
def create_ind_prod() -> None:
    """Cria os indicadores de produção do mês corrente e salva no banco de dados local."""

    try:
        # Obter os dados locais de produção
        df_production = production_controller.get_data()

        # Obter os dados locais de maquina IHM e Info
        df_info_ihm = info_ihm_controller.get_data()

        # Criar os indicadores de produção
        df_eff = ind_production.get_indicators(df_info_ihm, df_production, IndicatorType.EFFICIENCY)
        df_perf = ind_production.get_indicators(
            df_info_ihm, df_production, IndicatorType.PERFORMANCE
        )
        df_repair = ind_production.get_indicators(df_info_ihm, df_production, IndicatorType.REPAIR)

        # Salvar os indicadores no banco de dados local
        eff_controller.replace_data(df_eff)
        perf_controller.replace_data(df_perf)
        reparo_controller.replace_data(df_repair)
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar indicadores de produção: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar indicadores de produção: %s", e, exc_info=True)


# Função para manter histórico de indicadores de produção
def create_ind_history() -> None:
    """Cria o histórico de indicadores de produção e salva no banco de dados local."""
    try:
        # Obter as datas
        start, end = date_f.get_first_and_last_day_of_last_month()
        month = start.strftime("%Y-%m")
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")

        # Obter os dados de maquina info/ihm
        maq_ihm = maquina_ihm_controller.get_data((start, end))
        maq_info = maquina_info_controller.get_data((start, end))

        info_ihm_join = InfoIHMJoin(maq_ihm, maq_info)

        # Unir os dados de maquina IHM e info
        df_info_ihm = info_ihm_join.join_data()

        # Obter os dados da máquina Info e Qualidade
        prod = maquina_info_controller.get_production_data((start, end))
        qual = maquina_qualidade_controller.get_data((start, end))

        # Receber os produtos do protheus
        products_data = protheus_sb1_produtos_controller.get_data()

        # Juntar os dados de produção com os dados de qualidade e info
        df_prod = prod_qualid_join.join_data(qual, prod, products_data)

        # Criar os indicadores de produção
        df_eff = ind_production.get_indicators(df_info_ihm, df_prod, IndicatorType.EFFICIENCY)
        df_perf = ind_production.get_indicators(df_info_ihm, df_prod, IndicatorType.PERFORMANCE)
        df_repair = ind_production.get_indicators(df_info_ihm, df_prod, IndicatorType.REPAIR)

        # Atualiza ou cria o histórico de indicadores no banco de dados local
        historic_data = historic_ind_controller.get_data()

        # Verifica se o mês já está no histórico, se não atualiza ou cria os dados
        if month not in historic_data.data_registro.values:
            # Cria o histórico de indicadores
            df_history = hist_f.create_hist_ind(df_info_ihm, df_prod, df_eff, df_perf, df_repair)

            # Salva no banco de dados local
            historic_ind_controller.insert_data(df_history)
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar histórico de indicadores: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar histórico de indicadores: %s", e, exc_info=True)


# ================================================================================================ #
#                                      AGENDAMENTO DE TAREFAS                                      #
# ================================================================================================ #

# Inicializa o agendador de tarefas
scheduler = BackgroundScheduler()
HIGH_PRIORITY_INTERVAL = 1
LOW_PRIORITY_INTERVAL = 5
NON_CRITICAL_INTERVAL = 60

# Cria a tarefa de criação dos dados de produção do mês corrente
scheduler.add_job(
    create_production_data,
    "interval",
    minutes=LOW_PRIORITY_INTERVAL,
    start_date=datetime.now() + timedelta(seconds=5),
    max_instances=3,
)

# Cria a tarefa para criar os dados de maquina IHM e Info do mês corrente
scheduler.add_job(
    create_maq_ihm_info_data,
    "interval",
    minutes=HIGH_PRIORITY_INTERVAL,
    start_date=datetime.now() + timedelta(seconds=3),
    max_instances=3,
)

# Cria a tarefa para criar os indicadores de produção
scheduler.add_job(
    create_ind_prod,
    "interval",
    minutes=HIGH_PRIORITY_INTERVAL,
    start_date=datetime.now() + timedelta(seconds=1),
    max_instances=3,
)

# Cria a tarefa para criar o histórico de indicadores
scheduler.add_job(
    create_ind_history,
    "interval",
    minutes=NON_CRITICAL_INTERVAL,
    start_date=datetime.now() + timedelta(seconds=10),
    max_instances=1,
)

# Inicia o agendador
scheduler.start()
