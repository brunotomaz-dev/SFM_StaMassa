"""Módulo de Serviço para tabela com os dados de estoque."""

import pandas as pd

# pylint: disable=import-error
from src.model.protheus_sb2_estoque_model import ProtheusSB2EstoqueModel


class ProtheusSB2EstoqueService:
    """Classe de serviço para a tabela de estoque do protheus."""

    def __init__(self) -> None:
        self.__protheus_sb2_estoque = ProtheusSB2EstoqueModel()

    def get_data(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SB2_ESTOQUE."""
        data = self.__protheus_sb2_estoque.get_data()

        # Remover espaços vazios na string de produtos_id
        data.produto = data.produto.str.strip()

        return data
