""" Arquivo principal da aplicação Streamlit. """

import time

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator.utilities import (CredentialsError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               )
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="Shop Floor Management",
    layout="wide",
    page_icon=":material/edit:",
)

# Adicionar CSS personalizado para importar a fonte Poppins
# pylint: disable=w1514
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .sidebar-top {
    position: fixed;
    top: 0;
    left: 0;
    padding: 10px;
    text-align: left;
    font-size: 0.7vw;
}
    </style>
    """,
    unsafe_allow_html=True,
)
#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       inicializar state
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Inicializar state
if "role" not in st.session_state:
    st.session_state["role"] = None
if "add_user" not in st.session_state:
    st.session_state["add_user"] = False
if "pass_reset" not in st.session_state:
    st.session_state["pass_reset"] = False
if "page" not in st.session_state:
    st.session_state["page"] = None


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                         Authenticator
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# Lendo o arquivo de configuração
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Criando o objeto de autenticação
Hasher.hash_passwords(config['credentials'])

# Criando o objeto de autenticação
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ LOGIN ━━ #
# Criando o widget de login e recuperando os dados
nome: str | None = None
username: str | None = None
autenticado: bool = False
try:
    nome, autenticado, username = authenticator.login(
        location="sidebar", fields={'Form name':'Entrar', 'Username':'Email', 'Password':'Senha'}
    )
except LoginError as e:
    st.error(e)

# Verificando se o usuário foi autenticado
if autenticado:
    # Para ter botão de logout só na página Inicial
    if st.session_state["page"] == "Home":
        authenticator.logout(location="sidebar")
    st.sidebar.markdown(f'<div class="sidebar-top">Logado como: {nome}</div>', unsafe_allow_html=True)
elif autenticado is False:
    st.sidebar.error('Email/password incorreto')
elif autenticado is None:
    st.sidebar.warning('Por favor, preencha o email e a senha para logar')

# Recuperar o role do usuário
role = config['credentials']["usernames"][username]['role']

# Colocar o role no cookie
st.session_state['role'] = role

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ REGISTRAR USUÁRIO ━━ #
if st.session_state["add_user"]:
    try:
        (email_of_registered_user,
         username_of_registered_user,
         name_of_registered_user) = authenticator.register_user(
            pre_authorization=False,
            fields={
                'Username':'Confirmar Email',
                'Name':'Nome',
                "Repeat password":"Confirmar Senha",
                "Form name": "Registrar Usuário",
                "Register": "Registrar"
            }
        )
        if email_of_registered_user:
            st.toast('Usuário registrado com sucesso')
            st.success("Usuário registrado com sucesso")
            time.sleep(3)
            st.session_state["add_user"] = False
            st.rerun()
    except RegisterError as e:
        st.error(e)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ALTERAR SENHA ━━ #
if st.session_state["authentication_status"] and st.session_state["pass_reset"]:
    try:
        if authenticator.reset_password(st.session_state["username"],
            fields={
                "Form name": "Alterar Senha",
                "New password": "Nova Senha",
                "Repeat password": "Confirmar Nova Senha",
                "Current password": "Senha atual",
                "Reset": "Salvar"
            }):
            st.success('Senha alterada com sucesso')
            time.sleep(3)
            st.session_state["pass_reset"] = False
            st.rerun()
    except ResetError as e:
        st.error(e)
    except CredentialsError as e:
        st.error(e)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SALVAR ALTERAÇÕES DE LOGIN ━━ #
# Salvando o arquivo de configuração
with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)

# ================================================================================================ #
#                                               PAGES                                              #
# ================================================================================================ #

login_page = st.Page(
    page="app/pages/pg_login.py",
    title="Home",
    icon=":material/login:",
)

shop_floor_management_page = st.Page(
    page="app/pages/pg_sfm.py",
    title="Shop Floor Management",
    icon=":material/monitoring:",
)

all_lines_page = st.Page(
    page="app/pages/pg_all_lines.py",
    title="Ao Vivo",
    icon=":material/precision_manufacturing:",
)

per_hour_page = st.Page(
    page="app/pages/pg_prod_hour.py",
    title="Produção por hora",
    icon=":material/package_2:",
)

pcp_page = st.Page(
    page="app/pages/pg_pcp.py",
    title="PCP",
    icon=":material/production_quantity_limits:",
)

grafana_page = st.Page(
    page="app/pages/pg_grafana.py",
    title="NEW PAGE",
    icon=":material/live_tv:",
)

# ================================================================================================ #
#                                         LAYOUT AND CONFIG                                        #
# ================================================================================================ #
pg = None

if autenticado:
    if role in ["dev"]:
        pg = st.navigation([login_page, shop_floor_management_page, all_lines_page, per_hour_page, pcp_page, grafana_page])
    elif role == "pcp":
        pg = st.navigation([pcp_page, shop_floor_management_page, all_lines_page])
    elif role in ["coordenador", "coordenador-pcp", "gerente", "diretor"]:
        pg = st.navigation([shop_floor_management_page, all_lines_page, per_hour_page, pcp_page])
    elif role in ["lider", "supervisor"]:
        pg = st.navigation([shop_floor_management_page, all_lines_page, per_hour_page])
else:
    pg = st.navigation([login_page])

st.session_state["page"] = pg.title

pg.run()
