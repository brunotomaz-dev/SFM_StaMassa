"""Conexão com api Django"""

import requests


def api_get(url: str, token: str, params: str = None, data: dict = None):
    """
    Função para realizar requisições GET para a API.

    Args:
        url (str): URL da requisição.
        token (str): Token de autenticação.
        params (str, optional): Parâmetros da requisição. Defaults to None.
        data (dict, optional): Dados da requisição. Defaults to None.

    Returns:
        dict: Dados da resposta da API em formato JSON.
    """
    response = requests.get(
        url,
        params=params,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "content_type": "application/json",
        },
        timeout=10,
    )
    response.raise_for_status()  # Levanta uma exceção para códigos de status ruins
    data = response.json()
    return data


def api_post(url: str, params: str = None, data: dict = None, token: str = None):
    """
    Função para realizar requisições POST para a API.

    Args:
        url (str): URL da requisição.
        params (dict, optional): Parâmetros da requisição. Defaults to None.
        data (str, optional): Dados da requisição. Defaults to None.
        token (str, optional): Token de autenticação. Defaults to None.

    Returns:
        dict: Dados da resposta da API em formato JSON.
    """
    response = requests.post(
        url=url,
        params=params,
        data=data,
        headers=(
            {
                "Authorization": f"Bearer {token}",
                "content_type": "application/json",
            }
            if token
            else None
        ),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def api_get_token(username: str, password: str):
    """
    Função para obter um token de acesso da API.

    Args:
        username (str): Nome de usuário.
        password (str): Senha.

    Returns:
        str: Token de acesso.
    """
    token_url = "http://localhost:8000/api/token/"
    token = api_post(token_url, data={"username": username, "password": password})
    return token
