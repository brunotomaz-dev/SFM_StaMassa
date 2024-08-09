"""
Modulo para configurar os caminhos dos arquivos de dados (Gambiarra)
"""

import os

# Gambiarra para acessar arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/src/helpers
PARENT_DIR = os.path.dirname(CURRENT_DIR)  # backend/src
DB_DIR = os.path.join(PARENT_DIR, "database")  # backend/src/database

# Arquivos de dados
DB_LOCAL = os.path.join(DB_DIR, "automacao_local.db")
