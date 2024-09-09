"""Módulo de Controle para tabela de produtos do Protheus."""
import pandas as pd

# pylint: disable=import-error
from src.service.protheus_sb1_produtos_service import ProtheusSB1ProdutosService


class ProtheusSB1ProdutosController:
    """Classe de Controle para tabela de produtos do Protheus."""

    def __init__(self) -> None:
        self.__protheus_sb1_produtos_service = ProtheusSB1ProdutosService()

    def get_data(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SB1_PRODUTOS."""
        return self.__protheus_sb1_produtos_service.get_data()
