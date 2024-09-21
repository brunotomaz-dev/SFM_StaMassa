"""Módulo que gera uma data para pesquisas"""

from datetime import date, datetime

import pandas as pd


class GetDate:
    """Classe responsável por retornar datas, para evitar ficar travado em uma data."""

    def __init__(self) -> None:
        pass

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_today() -> datetime:
        """
        Retorna a data atual.

        Retorna:
        datetime: A data atual.
        """
        return pd.Timestamp("today")

    def get_this_turn(self) -> tuple[date, str]:
        """
        Retorna a data e o turno atual.

        Retorna:
        tuple[date, str]: Uma tupla contendo a data atual e o turno atual.
        O turno pode ser "NOT", "MAT" ou "VES".
        """
        today = self.get_today()

        if today.hour in range(0, 8):
            return today.date(), "NOT"
        elif today.hour in range(8, 16):
            return today.date(), "MAT"
        else:
            return today.date(), "VES"
