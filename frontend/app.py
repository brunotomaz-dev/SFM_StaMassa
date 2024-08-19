""" Arquivo principal da aplicação Streamlit. """

import streamlit as st

# ================================================================================================ #
#                                               PAGES                                              #
# ================================================================================================ #

shop_floor_management_page = st.Page(
    page="app/pages/pg_sfm.py", title="Shop Floor Management", icon=":material/monitoring:"
)

grafana_page = st.Page(
    page="app/pages/pg_grafana.py", title="Grafana Page", icon=":material/live_tv:"
)

# ================================================================================================ #
#                                         LAYOUT AN CONFIG                                         #
# ================================================================================================ #

pg = st.navigation([shop_floor_management_page, grafana_page])

st.set_page_config(page_title="Shop Floor Management", layout="wide", page_icon=":material/edit:")

pg.run()
