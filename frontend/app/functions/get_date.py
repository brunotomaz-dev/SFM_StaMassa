"""Módulo que gera uma data para pesquisas"""

from datetime import datetime

import pandas as pd


def get_this_month() -> tuple[datetime, datetime]:
    """
    Retorna o primeiro e o último dia do mês atual.

    Retorna:
    tuple[datetime, datetime]: Uma tupla contendo o primeiro e o último dia do mês atual.
    """
    today = pd.Timestamp("today")
    first_day = today.replace(day=1)
    last_day = today.replace(day=pd.Period(today, "M").days_in_month)

    return first_day, last_day


def get_last_month() -> tuple[datetime, datetime]:
    """
    Retorna o primeiro e o último dia do mês anterior.

    Retorna:
    tuple[datetime, datetime]: Uma tupla contendo o primeiro e o último dia do mês anterior.
    """
    today = pd.Timestamp("today")
    first_day_last_month = (today.replace(day=1) - pd.DateOffset(months=1)).date()
    last_day_last_month = (today.replace(day=1) - pd.DateOffset(days=1)).date()

    return first_day_last_month, last_day_last_month


def get_today() -> datetime:
    """
    Retorna a data atual.

    Retorna:
    datetime: A data atual.
    """
    return pd.Timestamp("today")
