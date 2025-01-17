""" Fonções que rodam em background, de forma agendada. """

import logging

import pandas as pd
from src.functions import date_f
from src.functions import history_functions as hist_f
from src.helpers.variables import IndicatorType
from src.service.action_plan_service import ActionPlanService
from src.service.efficiency_service import EfficiencyService
from src.service.functions.ind_prod import IndProd
from src.service.functions.info_ihm_join import InfoIHMJoin
from src.service.functions.prod_qualid_join import ProdQualidJoin
from src.service.historic_ind_service import HistoricIndService
from src.service.info_ihm import InfoIHMService
from src.service.maquina_ihm_service import MaquinaIHMService
from src.service.maquina_info_service import MaquinaInfoService
from src.service.maquina_qualidade_service import MaquinaQualidadeService
from src.service.performance_service import PerformanceService
from src.service.production_service import ProductionService
from src.service.protheus_sb1_produtos_service import ProtheusSB1ProdutosService
from src.service.reparo_service import ReparoService

maquina_ihm_service = MaquinaIHMService()
maquina_info_service = MaquinaInfoService()
maquina_qualidade_service = MaquinaQualidadeService()
protheus_sb1_produtos_service = ProtheusSB1ProdutosService()
production_service = ProductionService()
maquina_ihm_service = MaquinaIHMService()
info_ihm_service = InfoIHMService()
eff_service = EfficiencyService()
perf_service = PerformanceService()
reparo_service = ReparoService()
historic_ind_service = HistoricIndService()
prod_qualid_join = ProdQualidJoin()
ind_production = IndProd()
action_plan_service = ActionPlanService()

# Configura o logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Remove o warning de downcast do pandas
pd.set_option("future.no_silent_downcast", True)


# ======================================================================= Produção Do Mês Corrente #
def create_production_data() -> None:
    """Cria os dados de produção do mês corrente e salva no banco de dados local."""

    try:
        # Obter as datas do mês corrente
        start, end = date_f.get_first_and_last_day_of_month()
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")

        today = date_f.get_date()

        # obter a data de 31 dias antes da data de hoje
        start_31 = today - pd.DateOffset(days=31)
        start_31 = start_31.strftime("%Y-%m-%d")

        # Obter os dados da máquina Info e Qualidade
        prod = maquina_info_service.get_production_data((start_31, end))
        qual = maquina_qualidade_service.get_data((start_31, end))

        # Receber os produtos do protheus
        products_data = protheus_sb1_produtos_service.get_data()

        # Juntar os dados de produção com os dados de qualidade e info
        data = prod_qualid_join.join_data(qual, prod, products_data)

        # Salva no banco de dados local
        production_service.replace_data(data)

    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar dados de produção: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar dados de produção: %s", e, exc_info=True)


# ======================================================================== Criação De Máquina Info #
def create_maq_ihm_info_data() -> None:
    """Cria os dados de maquina IHM e Info e salva no banco de dados local."""

    try:
        # Obter as datas do mês corrente
        start, end = date_f.get_first_and_last_day_of_month()
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")

        today = date_f.get_date()

        # obter a data de 31 dias antes da data de hoje
        start_31 = today - pd.DateOffset(days=31)

        # Obter os dados da máquina Info e Qualidade
        maq_ihm = maquina_ihm_service.get_data((start_31, end))
        maq_info = maquina_info_service.get_data((start_31, end))

        info_ihm_join = InfoIHMJoin(maq_ihm, maq_info)

        # Unir os dados de maquina IHM e info
        data = info_ihm_join.join_data()

        # Salva no banco de dados local
        info_ihm_service.replace_data(data)
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar dados de maquina IHM e Info: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar dados de maquina IHM e Info: %s", e, exc_info=True)


# ============================================================ Criação Dos Indicadores De Produção #
def create_ind_prod() -> None:
    """Cria os indicadores de produção do mês corrente e salva no banco de dados local."""

    try:
        # Obter os dados locais de produção
        df_production = production_service.get_data()

        # Obter os dados locais de maquina IHM e Info
        df_info_ihm = info_ihm_service.get_data()

        # Criar os indicadores de produção
        df_eff = ind_production.get_indicators(df_info_ihm, df_production, IndicatorType.EFFICIENCY)
        df_perf = ind_production.get_indicators(
            df_info_ihm, df_production, IndicatorType.PERFORMANCE
        )
        df_repair = ind_production.get_indicators(df_info_ihm, df_production, IndicatorType.REPAIR)

        # Salvar os indicadores no banco de dados local
        eff_service.replace_data(df_eff)
        perf_service.replace_data(df_perf)
        reparo_service.replace_data(df_repair)
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar indicadores de produção: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar indicadores de produção: %s", e, exc_info=True)


# =========================================================== Criação Do Histórico Dos Indicadores #
def create_ind_history() -> None:
    """Cria o histórico de indicadores de produção e salva no banco de dados local."""
    try:
        # Obter as datas
        start, end = date_f.get_first_and_last_day_of_last_month()
        month = start.strftime("%Y-%m")
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")

        # Obter os dados de maquina info/ihm
        maq_ihm = maquina_ihm_service.get_data((start, end))
        maq_info = maquina_info_service.get_data((start, end))

        info_ihm_join = InfoIHMJoin(maq_ihm, maq_info)

        # Unir os dados de maquina IHM e info
        df_info_ihm = info_ihm_join.join_data()

        # Obter os dados da máquina Info e Qualidade
        prod = maquina_info_service.get_production_data((start, end))
        qual = maquina_qualidade_service.get_data((start, end))

        # Receber os produtos do protheus
        products_data = protheus_sb1_produtos_service.get_data()

        # Juntar os dados de produção com os dados de qualidade e info
        df_prod = prod_qualid_join.join_data(qual, prod, products_data)

        # Criar os indicadores de produção
        df_eff = ind_production.get_indicators(df_info_ihm, df_prod, IndicatorType.EFFICIENCY)
        df_perf = ind_production.get_indicators(df_info_ihm, df_prod, IndicatorType.PERFORMANCE)
        df_repair = ind_production.get_indicators(df_info_ihm, df_prod, IndicatorType.REPAIR)

        # Atualiza ou cria o histórico de indicadores no banco de dados local
        historic_data = historic_ind_service.get_data()

        # Verifica se o mês já está no histórico, se não atualiza ou cria os dados
        if month not in historic_data.data_registro.values:
            # Cria o histórico de indicadores
            df_history = hist_f.create_hist_ind(df_info_ihm, df_prod, df_eff, df_perf, df_repair)

            # Salva no banco de dados local
            historic_ind_service.insert_data(df_history)
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao criar histórico de indicadores: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao criar histórico de indicadores: %s", e, exc_info=True)


def update_action_plan() -> None:
    """Atualiza os dias em aberto da tabela de plano de ação."""

    try:
        # Obter dados
        df_action_plan = action_plan_service.get_data()

        # Garantir que conclusão seja um bool
        df_action_plan["Conclusao"] = df_action_plan["Conclusao"].astype(bool)

        # Manter apenas onde a coluna 'conclusão' seja false
        df_action_plan = df_action_plan[~df_action_plan["Conclusao"]]

        # Atualizar os dias em abertos
        df_action_plan["Dias_em_Aberto"] = abs(
            (pd.to_datetime(df_action_plan["Data"]) - pd.Timestamp("today").normalize()).dt.days
        )

        # Garantir que os dias em aberto sejam inteiros
        df_action_plan["Dias_em_Aberto"] = df_action_plan["Dias_em_Aberto"].astype(int)

        # Pegar os indexes dos dias em aberto
        index = df_action_plan.index.tolist()

        # Criar uma lista de dict com dados alterados
        data = [{"Dias_em_Aberto": df_action_plan.loc[i, "Dias_em_Aberto"]} for i in index]

        # Atualizar o DB
        action_plan_service.update_data(index, data)
    except (ValueError, KeyError, TypeError) as e:
        logger.error("Erro ao atualizar os dias em aberto: %s", e)
    # pylint: disable=w0718
    except Exception as e:
        logger.error("Erro inesperado ao atualizar os dias em aberto: %s", e, exc_info=True)
