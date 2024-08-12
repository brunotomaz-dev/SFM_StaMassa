"""Módulo com funções auxiliares de data."""

from datetime import datetime

import pandas as pd


def get_first_and_last_day_of_month() -> tuple[datetime, datetime]:
    """
    Retorna o primeiro e o último dia do mês de uma data.

    Parâmetros:
    date (datetime): A data.

    Retorna:
    tuple[datetime, datetime]: Uma tupla contendo o primeiro e o último dia do mês.
    """
    today = pd.Timestamp("today")
    first_day = today.replace(day=1)
    last_day = today.replace(day=pd.Period(today, "M").days_in_month)

    return first_day, last_day


def get_first_and_last_day_of_last_month() -> tuple[datetime, datetime]:
    """
    Retorna o primeiro e o último dia do mês anterior.

    Retorna:
    tuple[datetime, datetime]: Uma tupla contendo o primeiro e o último dia do mês anterior.
    """
    today = pd.Timestamp("today")
    first_day_last_month = (today.replace(day=1) - pd.DateOffset(months=1)).date()
    last_day_last_month = (today.replace(day=1) - pd.DateOffset(days=1)).date()

    return first_day_last_month, last_day_last_month


def get_date():
    """
    Retorna a data atual.

    Retorna:
    datetime: A data atual.
    """
    return pd.Timestamp("today")
