""" Arquivo principal da aplicação Streamlit. """

import asyncio
import time
from datetime import datetime, timedelta

import streamlit as st
import streamlit_authenticator as stauth
import yaml

# pylint: disable=E0401
from app.api.fetch_api import update_api
from streamlit_authenticator.utilities import (
    CredentialsError,
    Hasher,
    LoginError,
    RegisterError,
    ResetError,
)
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="Shop Floor Management",
    layout="wide",
    page_icon="assets/favicon.ico",
)
# Adicionar CSS personalizado para importar a fonte Poppins
# pylint: disable=w1514
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                       Inicializar State
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
if "api_running" not in st.session_state:
    st.session_state["api_running"] = False
if "last_api_call" not in st.session_state:
    st.session_state["last_api_call"] = datetime.min


# ================================================================================================ #
#                                         REQUISIÇÃO DE API                                        #
# ================================================================================================ #


@st.fragment(run_every=60)
def api_session_update() -> None:
    """
    Função que atualiza os dados da API a cada 60 segundos.

    Verifica se a chamada foi recente, caso sim, retorna. Caso contrário,
    atualiza o estado de 'last_api_call' para a data e hora atual e faz
    a requisição da API. O resultado é armazenado nas chaves da API/State.
    """
    progress = st.empty()
    # Encontra a data e hora atual
    now = datetime.now()

    # Verifica se a chamada foi recente, caso sim, retorna
    if now - st.session_state.last_api_call < timedelta(seconds=60):
        return

    # Atualiza o progresso
    progress.progress(value=0, text="Atualizando dados...")

    # Seta o estado de 'last_api_call' para a data e hora atual
    st.session_state["last_api_call"] = now

    # Atualiza o progresso
    progress.progress(25, "Atualizando dados...")

    # Faz a requisição da API
    result = asyncio.run(update_api())

    # Atualiza o progresso
    progress.progress(50, "Atualizando dados...")
    # Chaves da API/State
    keys = [
        "produção",
        "caixas_estoque",
        "eficiência",
        "performance",
        "reparos",
        "info_ihm",
        "hist_ind",
        "maquina_info_today",
        "cart_entering_greenhouse",
    ]

    # Corre as chaves e armazena os resultados se existirem
    for key, res in zip(keys, result):
        prog = 50 + 50 * (keys.index(key) + 1) / len(keys)
        progress.progress(int(prog), "Atualizando dados...")
        if not res.empty:
            st.session_state[key] = res

    # Atualiza o progresso
    progress.progress(100, "Dados atualizados")
    time.sleep(2)

    # Remove o progresso
    progress.empty()


# Chaves do State a serem verificadas
keys_to_check = [
    "produção",
    "caixas_estoque",
    "eficiência",
    "performance",
    "reparos",
    "info_ihm",
    "hist_ind",
    "maquina_info_today",
    "cart_entering_greenhouse",
]

# Faz a verificação das chaves, caso não existam, faz a requisição
if any(key not in st.session_state for key in keys_to_check):
    api_session_update()

#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#                                         Authenticator
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# Lendo o arquivo de configuração
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Criando o objeto de autenticação
Hasher.hash_passwords(config["credentials"])

# Criando o objeto de autenticação
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["pre-authorized"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SALVAR ALTERAÇÕES DE LOGIN ━━ #
# Salvando o arquivo de configuração
def save_config(c: dict) -> None:
    """Salva as alterações feitas no arquivo de configuração."""
    with open("config.yaml", "w") as f:
        yaml.dump(c, f, default_flow_style=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ LOGIN ━━ #
# Criando o widget de login e recuperando os dados
nome: str | None = None
username: str | None = None
autenticado: bool = False
try:
    nome, autenticado, username = authenticator.login(
        location="sidebar", fields={"Form name": "Entrar", "Username": "Email", "Password": "Senha"}
    )
except LoginError as e:
    st.error(e)

# Verificando se o usuário foi autenticado
if autenticado:
    # Para ter botão de logout só na página Inicial
    if st.session_state["page"] == "Home":
        authenticator.logout(location="sidebar")
    # Recuperar o role do usuário
    role = config["credentials"]["usernames"][username]["role"]
    # Colocar o role no cookie
    st.session_state["role"] = role
elif autenticado is False:
    st.sidebar.error("Email/password incorreto")
elif autenticado is None:
    st.sidebar.warning("Por favor, preencha o email e a senha para logar")

if st.session_state["username"] is None:
    st.session_state["role"] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ REGISTRAR USUÁRIO ━━ #
if st.session_state["add_user"]:
    try:
        (email_of_registered_user, username_of_registered_user, name_of_registered_user) = (
            authenticator.register_user(
                pre_authorization=False,
                fields={
                    "Username": "Confirmar Email",
                    "Name": "Nome",
                    "Repeat password": "Confirmar Senha",
                    "Form name": "Registrar Usuário",
                    "Register": "Registrar",
                },
            )
        )
        if email_of_registered_user:
            save_config(config)
            st.toast("Usuário registrado com sucesso")
            st.success("Usuário registrado com sucesso")
            time.sleep(3)
            st.session_state["add_user"] = False
            st.rerun()
    except RegisterError as e:
        st.error(e)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ALTERAR SENHA ━━ #
pass_fields = {
    "Form name": "Alterar Senha",
    "New password": "Nova Senha",
    "Repeat password": "Confirmar Nova Senha",
    "Current password": "Senha atual",
    "Reset": "Salvar",
}


def handle_password_reset():
    """
    Função para lidar com a redefinição de senha.
    """
    try:
        if authenticator.reset_password(st.session_state["username"], fields=pass_fields):
            save_config(config)
            st.success("Senha alterada com sucesso")
            time.sleep(3)
            st.session_state["pass_reset"] = False
            st.rerun()
    except ResetError as err:
        st.error(err)
    except CredentialsError as err:
        st.error(err)


if st.session_state["authentication_status"] and st.session_state["pass_reset"]:
    handle_password_reset()

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
    title="Linhas Ao Vivo",
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

all_lines_hist_page = st.Page(
    page="app/pages/pg_all_lines_hist.py",
    title="Linhas Histórico",
    icon=":material/history:",
)

management_page = st.Page(
    page="app/pages/pg_management.py",
    title="Gestão",
    icon=":material/manage_history:",
)


# ================================================================================================ #
#                                         LAYOUT AND CONFIG                                        #
# ================================================================================================ #
PG = None


def get_navigation(user_role):
    """
    Retorna a navegação do usuário com base em seu cargo.
    """

    # Conjuntos de páginas para reutilização
    paginas_basicas = [login_page]
    paginas_lider_supervisor = paginas_basicas + [
        shop_floor_management_page,
        per_hour_page,
        all_lines_page,
    ]
    paginas_coordenacao = paginas_lider_supervisor + [all_lines_hist_page, management_page]
    # paginas_coordenacao_pcp = paginas_coordenacao + [pcp_page]
    paginas_pcp = paginas_basicas + [pcp_page]
    paginas_dev = paginas_coordenacao

    # Mapeamento de roles para listas de páginas
    role_pages = {
        "dev": paginas_dev,
        "pcp": paginas_pcp,
        "coordenador": paginas_coordenacao,
        # "coordenador-pcp": paginas_coordenacao_pcp,
        "coordenador-pcp": paginas_coordenacao,
        "gerente": paginas_coordenacao,
        "diretor": paginas_coordenacao,
        "lider": paginas_lider_supervisor,
        "supervisor": paginas_lider_supervisor + [all_lines_hist_page],
    }

    # Retorna a lista de páginas correspondente ao role ou a página de login por padrão
    return st.navigation(role_pages.get(user_role, paginas_basicas))


if autenticado:
    PG = get_navigation(role)
else:
    PG = st.navigation([login_page])

st.session_state["page"] = PG.title

PG.run()

api_session_update()
