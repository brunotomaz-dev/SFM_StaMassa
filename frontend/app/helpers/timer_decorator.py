import time
from functools import wraps

import streamlit as st


def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Converter para milissegundos
        st.write(f"Tempo de execução de {func.__name__}: {execution_time:.2f}ms")
        return result

    return wrapper
