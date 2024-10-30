"""Módulo com o modelo de resposta de erro."""

from typing import List, Union

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Modelo de detalhes de erro."""

    loc: List[Union[str, int]]
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Modelo de resposta de erro."""

    detail: List[ErrorDetail]
