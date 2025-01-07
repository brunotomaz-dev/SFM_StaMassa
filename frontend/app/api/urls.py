"""Módulo com urls da API."""

from enum import Enum

# class APIUrl(Enum):
#     """
#     Enum com as urls da API.

#     Attributes:
#     - URL_MAQ_IHM (str): URL da API que retorna os dados da máquina IHM.
#         Precisa de dois parâmetros: start (str) e end (str).
#     - URL_MAQ_INFO (str): URL da API que retorna os dados da máquina Info.
#         Precisa de dois parâmetros: start (str) e end (str).
#     - URL_MAQ_PROD (str): URL da API que retorna os dados de produção da máquina Info.
#         Precisa de dois parâmetros: start (str) e end (str).

#     Exemplo de URL:
#     http://localhost:8000/maquina_ihm?start=2022-01-01&end=2022-01-31

#     Exemplo de Uso:
#     "f"{APIUrl.URL_MAQ_IHM.value}?start=2022-01-01&end=2022-01-31"
#     "http://localhost:8000/maquina_ihm?start=2022-01-01&end=2022-01-31"
#     """

#     URL_MAQ_IHM = "http://192.168.0.121:8000/machine/maquina_ihm"
#     URL_MAQ_INFO = "http://192.168.0.121:8000/machine/maquina_info"
#     URL_MAQ_QUALIDADE = "http://192.168.0.121:8000/machine/maquina_qualidade"
#     URL_PROD = "http://192.168.0.121:8000/local/production"
#     URL_INFO_IHM = "http://192.168.0.121:8000/local/info_ihm"
#     URL_EFF = "http://192.168.0.121:8000/local/efficiency"
#     URL_PERF = "http://192.168.0.121:8000/local/performance"
#     URL_REP = "http://192.168.0.121:8000/local/reparo"
#     URL_HIST_IND = "http://192.168.0.121:8000/local/historic_ind"
#     URL_MASSA = "http://192.168.0.121:8000/protheus_cyv/massa"
#     URL_MASSA_WEEK = "http://192.168.0.121:8000/protheus_cyv/massa_week"
#     URL_PASTA = "http://192.168.0.121:8000/protheus_cyv/pasta"
#     URL_PASTA_WEEK = "http://192.168.0.121:8000/protheus_cyv/pasta_week"
#     URL_CART_GREENHOUSE = "http://192.168.0.121:8000/protheus_cyv/cart_entering_greenhouse"
#     URL_CAIXAS_CF = "http://192.168.0.121:8000/protheus_sd3/production"
#     URL_PCP_ESTOQUE = "http://192.168.0.121:8000/protheus_sd3/pcp_estoque"
#     URL_CAIXAS_ESTOQUE = "http://192.168.0.121:8000/protheus_sb2/caixas_estoque"
#     URL_ACTION_PLAN = "http://192.168.0.121:8000/local/action_plan"
#     URL_MAQ_INFO_PURE = "http://192.168.0.121:8000/machine/maquina_info_pure"


class APIUrl(Enum):
    """
    A ser usado em testes
    """

    URL_MAQ_IHM = "http://localhost:8000/machine/maquina_ihm"
    URL_MAQ_INFO = "http://localhost:8000/machine/maquina_info"
    URL_MAQ_QUALIDADE = "http://localhost:8000/machine/maquina_qualidade"
    URL_PROD = "http://localhost:8000/local/production"
    URL_INFO_IHM = "http://localhost:8000/local/info_ihm"
    URL_EFF = "http://localhost:8000/local/efficiency"
    URL_PERF = "http://localhost:8000/local/performance"
    URL_REP = "http://localhost:8000/local/reparo"
    URL_HIST_IND = "http://localhost:8000/local/historic_ind"
    URL_MASSA = "http://localhost:8000/protheus_cyv/massa"
    URL_MASSA_WEEK = "http://localhost:8000/protheus_cyv/massa_week"
    URL_PASTA = "http://localhost:8000/protheus_cyv/pasta"
    URL_PASTA_WEEK = "http://localhost:8000/protheus_cyv/pasta_week"
    URL_CART_GREENHOUSE = "http://localhost:8000/protheus_cyv/cart_entering_greenhouse"
    URL_CAIXAS_CF = "http://localhost:8000/protheus_sd3/production"
    URL_PCP_ESTOQUE = "http://localhost:8000/protheus_sd3/pcp_estoque"
    URL_CAIXAS_ESTOQUE = "http://localhost:8000/protheus_sb2/caixas_estoque"
    URL_ACTION_PLAN = "http://localhost:8000/local/action_plan"
    URL_MAQ_INFO_PURE = "http://localhost:8000/machine/maquina_info_pure"
