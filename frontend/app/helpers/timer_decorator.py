"""
Este módulo fornece um decorador para medir o tempo de execução de funções.
"""

import time
from functools import wraps


def timer_decorator(func):
    """
    Um decorador que mede o tempo de execução de uma função e imprime o resultado.

    Args:
        func: A função a ser decorada.

    Returns:
        A função decorada.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Converter para milissegundos
        print(f"Tempo de execução de {func.__name__}: {execution_time:.2f}ms")
        return result

    return wrapper
