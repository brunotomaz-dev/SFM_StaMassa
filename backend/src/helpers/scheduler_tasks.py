"""
Módulo agendador de tarefas.
CreatedAT: 09/08/2024
CreatedBy: Bruno Tomaz
"""

from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
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
HIGH_PRIORITY_INTERVAL = 1
LOW_PRIORITY_INTERVAL = 5
NON_CRITICAL_INTERVAL = 60
DAILY_INTERVAL = 60 * 24


# Iniciar o agendador
def start_scheduler() -> None:
    """
    Inicia o planejador de tarefas em segundo plano para gerenciar várias atividades periódicas.
    A função agenda as seguintes tarefas para execução em intervalos específicos:

    - Geração de dados de produção do mês atual: programada com prioridade baixa.
    - Geração de dados para IHM e informações da máquina: programada com prioridade alta.
    - Criação de indicadores de produção: programada com prioridade alta.
    - Criação de histórico de indicadores: programada com prioridade não crítica.
    Cada tarefa é configurada com um atraso inicial e um limite para o número de instâncias
    simultâneas em execução.
    """

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

    # Cria a tarefa para atualizar o plano de ação
    scheduler.add_job(
        update_action_plan,
        "interval",
        minutes=DAILY_INTERVAL,
        start_date=datetime.now() + timedelta(seconds=10),
        max_instances=1,
    )

    # Inicia o agendador
    scheduler.start()
