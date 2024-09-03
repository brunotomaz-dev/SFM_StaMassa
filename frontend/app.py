""" Arquivo principal da aplicação Streamlit. """

import streamlit as st

st.set_page_config(
    page_title="Shop Floor Management",
    layout="wide",
    page_icon=":material/edit:",
)

# Adicionar CSS personalizado para importar a fonte Poppins
# pylint: disable=w1514
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# ================================================================================================ #
#                                               PAGES                                              #
# ================================================================================================ #

shop_floor_management_page = st.Page(
    page="app/pages/pg_sfm.py",
    title="Shop Floor Management",
    icon=":material/monitoring:",
)

grafana_page = st.Page(
    page="app/pages/pg_grafana.py",
    title="NEW PAGE",
    icon=":material/live_tv:",
)

all_lines_page = st.Page(
    page="app/pages/pg_all_lines.py",
    title="All Lines",
    icon=":material/precision_manufacturing:",
)

# ================================================================================================ #
#                                         LAYOUT AN CONFIG                                         #
# ================================================================================================ #

pg = st.navigation([shop_floor_management_page, all_lines_page, grafana_page])

pg.run()
