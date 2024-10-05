"""Módulo que contém a página de visualização de todas as linhas de um histograma."""

import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import fetch_api_data
from app.api.urls import APIUrl
