"""Módulo de serviço para tabela de produtos do Protheus."""
import pandas as pd

# pylint: disable=import-error
from src.model.protheus_sb1_produtos_model import ProtheusSB1ProdutosModel


class ProtheusSB1ProdutosService:
    """Classe de serviço para tabela de produtos do Protheus."""

    def __init__(self) -> None:
        self.__protheus_sb1_produtos = ProtheusSB1ProdutosModel()

    def get_data(self) -> pd.DataFrame:
        """Retorna os dados da tabela PROTHEUS_SB1_PRODUTOS."""
        data = self.__protheus_sb1_produtos.get_data()

        # Remover espaços vazios na string de produtos_id
        data.produto_id = data.produto_id.str.strip()

        # Remover espaços vazios na string de descricao
        data.descricao = data.descricao.str.strip()

        # Remover valores em que produto_id tem mais de 8 caracteres
        data = data[data.produto_id.str.len() <= 8]

        return data
