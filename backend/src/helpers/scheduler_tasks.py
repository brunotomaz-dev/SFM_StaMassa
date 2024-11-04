"""
Módulo agendador de tarefas.
CreatedAT: 09/08/2024
CreatedBy: Bruno Tomaz
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

# pylint: disable=import-error
from src.helpers.background_functions import (
    create_ind_history,
    create_ind_prod,
    create_maq_ihm_info_data,
    create_production_data,
    update_action_plan,
)

# ================================================================================================ #
#                                      AGENDAMENTO DE TAREFAS                                      #
# ================================================================================================ #

# Inicializa o agendador de tarefas
scheduler = BackgroundScheduler()
executor = ThreadPoolExecutor(max_workers=10)
HIGH_PRIORITY_INTERVAL = 1
LOW_PRIORITY_INTERVAL = 5
NON_CRITICAL_INTERVAL = 60
DAILY_INTERVAL = 60 * 24


async def run_in_executor(func, *args):
    """Executa uma função em um executor de thread em segundo plano.

    Args:
        func: Função a ser executada.
        *args: Argumentos a serem passados para a função.

    Returns:
        O resultado da execução da função.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


# Iniciar o agendador
def start_scheduler() -> None:
    """Inicia o agendador de tarefas.

    O agendador de tarefas será iniciado com as seguintes tarefas:

    - Criação dos dados de produção do mês corrente a cada 5 minutos
    - Criação dos dados de maquina IHM e Info do mês corrente a cada 1 minutos
    - Criação dos indicadores de produção a cada 1 minutos
    - Criação do histórico de indicadores a cada 1 hora
    - Atualização do plano de ação diariamente às 0h00

    O agendador irá rodar em segundo plano e as tarefas serão executadas em threads separados
    utilizando o executor de threads.
    """

    # Cria a tarefa de criação dos dados de produção do mês corrente
    scheduler.add_job(
        lambda: asyncio.run(run_in_executor(create_production_data)),
        "interval",
        minutes=5,
        start_date=datetime.now() + timedelta(seconds=5),
        max_instances=3,
    )

    # Cria a tarefa para criar os dados de maquina IHM e Info do mês corrente
    scheduler.add_job(
        lambda: asyncio.run(run_in_executor(create_maq_ihm_info_data)),
        "interval",
        minutes=1,
        start_date=datetime.now() + timedelta(seconds=5),
        max_instances=3,
    )

    # Cria a tarefa para criar os indicadores de produção
    scheduler.add_job(
        lambda: asyncio.run(run_in_executor(create_ind_prod)),
        "interval",
        minutes=1,
        start_date=datetime.now() + timedelta(seconds=5),
        max_instances=3,
    )

    # Cria a tarefa para criar o histórico de indicadores
    scheduler.add_job(
        lambda: asyncio.run(run_in_executor(create_ind_history)),
        "interval",
        hours=1,
        start_date=datetime.now() + timedelta(seconds=5),
        max_instances=3,
    )

    # Cria a tarefa para atualizar o plano de ação
    scheduler.add_job(
        lambda: asyncio.run(run_in_executor(update_action_plan)),
        "cron",
        hour=0,
        minute=0,
        start_date=datetime.now() + timedelta(seconds=5),
        max_instances=3,
    )

    # Inicia o agendador
    scheduler.start()
