""" Módulo para plano d e ação """

import asyncio

import pandas as pd
import streamlit as st

# pylint: disable=import-error
from app.api.requests_ import delete_api_data, fetch_api_data, insert_api_data, update_api_data
from app.api.urls import APIUrl

# ================================================================================================ #
#                                            API HANDLE                                            #
# ================================================================================================ #


async def insert_action_plan(dict_list: list[dict]) -> None:
    """Insere os dados na tabela de plano de ação."""
    await insert_api_data(APIUrl.URL_ACTION_PLAN.value, dict_list)


@st.cache_data(ttl=60 * 5, show_spinner="Carregando dados...")
def fetch_action_plan() -> pd.DataFrame:
    """Busca os dados da tabela de plano de ação."""
    return asyncio.run(fetch_api_data(APIUrl.URL_ACTION_PLAN.value))


def delete_action_plan(list_index: dict) -> None:
    """Deleta os dados da tabela de plano de ação."""
    asyncio.run(delete_api_data(APIUrl.URL_ACTION_PLAN.value, list_index))


def update_action_plan(index: list[int], dict_list: list[dict]) -> None:
    """Atualiza os dados da tabela de plano de ação."""
    asyncio.run(update_api_data(APIUrl.URL_ACTION_PLAN.value, index, dict_list))


# ================================================================================================ #
#                                            DATAFRAMES                                            #
# ================================================================================================ #


action_plan_model_df = pd.DataFrame(
    columns=[
        "Data",
        "Indicador",
        "Dias_em_Aberto",
        "Prioridade",
        "Turno",
        "Descricao_do_Problema",
        "Impacto",
        "Causa_Raiz",
        "Contencao",
        "Solucao",
        "Feedback",
        "Responsavel",
        "Conclusao",
    ],
)


def edit_action() -> None:
    """Toggle de edição da tabela de plano de ação."""
    st.session_state.edit_action = not st.session_state.edit_action


def add_action() -> None:
    """Adiciona as linhas adicionadas, remove as linhas excluídas e salva as alterações
    feitas na tabela de plano de ação."""
    alt_table = st.session_state.action_plan
    handle_added_rows(alt_table)
    handle_deleted_rows(alt_table)
    handle_edited_rows(alt_table)
    st.session_state.edit_action = False


def save_action(df: pd.DataFrame) -> None:
    """Salva as adições feitas pelo formulário."""
    df_adjusted = df.copy()
    df_adjusted["Data"] = pd.to_datetime(df_adjusted["Data"]).dt.strftime("%Y-%m-%d")
    dict_to_save = df_adjusted.to_dict(orient="records")
    asyncio.run(insert_action_plan(dict_to_save))

    st.session_state.table_action = pd.concat(
        [st.session_state.table_action, df], ignore_index=True
    )
    add_action_form()
    st.rerun()


def add_action_form() -> None:
    """Toggle de edição da tabela de plano de ação."""
    st.session_state.add_action = not st.session_state.add_action


def handle_added_rows(alt_table: list[dict]) -> None:
    """Adiciona as linhas adicionadas na edição da tabela de plano de ação.

    Essa função pega as linhas que foram adicionadas na edição da tabela e
    as concatena com a tabela original de plano de ação.

    Args:
        alt_table (pd.DataFrame): A tabela editada com as linhas adicionadas.
    """
    if len(alt_table["added_rows"]) > 0:
        expected_columns = action_plan_model_df.columns
        df = pd.DataFrame(columns=expected_columns)
        for row in alt_table["added_rows"]:
            add_row = pd.DataFrame([row], columns=expected_columns)
            add_row["Impacto"] = add_row["Impacto"].fillna(0).astype(float)
            add_row = add_row.fillna("")
            add_row["Dias_em_Aberto"] = abs(
                (pd.to_datetime(add_row["Data"]) - pd.Timestamp("today").normalize()).dt.days
            )
            df = pd.concat([df, add_row], ignore_index=True)
        list_of_dicts = df.to_dict(orient="records")
        asyncio.run(insert_action_plan(list_of_dicts))

        st.session_state.table_action = pd.concat(
            [st.session_state.table_action, pd.DataFrame(df)],
            ignore_index=True,
        )


def handle_deleted_rows(alt_table: pd.DataFrame) -> None:
    """Remove as linhas excluídas na edição da tabela de plano de ação.

    Essa função pega as linhas que foram excluídas na edição da tabela e
    as remove da tabela original de plano de ação.
    """
    if len(alt_table["deleted_rows"]) > 0:
        delete_action_plan(alt_table["deleted_rows"])

        st.session_state.table_action = st.session_state.table_action.drop(
            alt_table["deleted_rows"], axis=0
        )
        st.session_state.table_action = st.session_state.table_action.reset_index(drop=True)


def handle_edited_rows(alt_table: pd.DataFrame) -> None:
    """Salva as alterações feitas na edição da tabela de plano de ação.

    Essa função pega as alterações feitas na edição da tabela e as aplica na
    tabela original de plano de ação.
    """
    if len(alt_table["edited_rows"]) > 0:
        keys = list(alt_table["edited_rows"].keys())
        values = list(alt_table["edited_rows"].values())
        update_action_plan(keys, values)

        for str_idx, changes in alt_table["edited_rows"].items():
            idx = int(str_idx)
            for col, new_value in changes.items():
                st.session_state.table_action.at[idx, col] = new_value


def session_state_start(df: pd.DataFrame) -> None:
    """
    Initializes session state variables related to the action plan.

    This function checks if specific keys related to the action plan are present
    in the Streamlit session state. If not, it initializes them with default values:
    - 'edit_action': a boolean indicating whether the action plan is in edit mode.
    - 'add_action': a boolean indicating whether a new action is being added.
    - 'table_action': a DataFrame to store the action plan details with predefined columns.
    """
    # Inicializar State
    if "edit_action" not in st.session_state:
        st.session_state.edit_action = False

    if "add_action" not in st.session_state:
        st.session_state.add_action = False

    if "table_action" not in st.session_state or st.session_state.table_action.empty:
        st.session_state.table_action = df if not df.empty else action_plan_model_df


# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #


def action_plan(date_choice: str | None) -> None:
    """Plano de ação."""
    action_plan_df = fetch_action_plan()

    # Inicializar State
    session_state_start(action_plan_df)

    # Tabela
    df_action = st.session_state.table_action

    if date_choice:
        date_choice = pd.Timestamp(date_choice)
        df_action["Data"] = pd.to_datetime(df_action["Data"])
        st.write(date_choice)
        st.write(df_action["Data"])
        df_action = df_action[df_action["Data"] == date_choice]

    config = {
        "Data": st.column_config.DateColumn(format="DD/MM/YYYY", default=pd.Timestamp("today")),
        "Indicador": st.column_config.SelectboxColumn(options=["S", "Q", "D", "C"]),
        "Dias_em_Aberto": st.column_config.NumberColumn(label="Dias em aberto"),
        "Prioridade": st.column_config.SelectboxColumn(options=[1, 2, 3]),
        "Turno": st.column_config.SelectboxColumn(options=["Matutino", "Vespertino", "Noturno"]),
        "Descricao_do_Problema": st.column_config.TextColumn(label="Descricão do problema"),
        "Impacto": st.column_config.NumberColumn(
            format="%.1f%%",
            min_value=0,
            max_value=100,
            help="Impacto em porcentagem",
            label="Impacto %",
        ),
        "Contencao": st.column_config.TextColumn(label="Contenção"),
        "Causa_Raiz": st.column_config.TextColumn(label="Causa raiz"),
        "Solucao": st.column_config.TextColumn(label="Solução"),
        "Feedback": st.column_config.TextColumn(),
        "Responsavel": st.column_config.TextColumn(label="Responsável"),
        "Conclusao": st.column_config.CheckboxColumn(default=False, label="Conclusão"),
    }

    # Tabela
    if st.session_state.edit_action:
        with st.form(key="action_plan_form"):
            st.write("Plano de ação - Em edição")
            df_action["Data"] = pd.to_datetime(df_action["Data"]).dt.date
            st.data_editor(
                df_action,
                column_config=config,
                num_rows="dynamic",
                key="action_plan",
                use_container_width=True,
            )
            st.form_submit_button("Salvar", on_click=add_action)
    else:
        st.write("Plano de ação")
        df_action_filtered = df_action[df_action["Conclusao"] == 0]

        st.dataframe(
            df_action_filtered, use_container_width=True, column_config=config, hide_index=True
        )

    # Botões
    with st.sidebar:
        st.subheader("Plano de Ação")
        side_col, side_col_2 = st.columns(2)
        side_col.button("Editar", on_click=edit_action, use_container_width=True)
        side_col_2.button("Adicionar", on_click=add_action_form, use_container_width=True)

    if st.session_state.add_action:
        with st.form(key="form_add_action", clear_on_submit=True):
            st.write("Plano de ação - Adicionar")
            form_col1, form_col2, form_col3, form_col4, form_col9 = st.columns(5)
            form_col5, form_col6 = st.columns(2)
            form_col7, form_col8 = st.columns(2)
            # Coleta dos dados
            f1 = form_col1.date_input("Data", format="DD/MM/YYYY", value=pd.Timestamp("today"))
            f2 = form_col2.selectbox("Indicador", options=["S", "Q", "D", "C"])
            # Dias em aberto é calculado automaticamente.
            today_date = pd.Timestamp("today")
            f3 = (pd.to_datetime(f1) - pd.to_datetime(today_date)).days
            # Mudar o sinal pra ficar positivo
            f3 = abs(f3)
            f4 = form_col3.selectbox("Prioridade", options=[1, 2, 3])
            f13 = form_col9.selectbox("Turno", options=["Matutino", "Vespertino", "Noturno"])
            problema_help = (
                "Problema - Explicar porque parou(do ponto de vista da produção)"
                " e porque não atingiu a meta"
            )
            f5 = (
                form_col5.text_area(
                    "Descrição do Problema",
                    height=207,
                    placeholder="Incluir a máquina, linha, produto, setor e problema",
                    help=problema_help,
                ),
            )
            f6 = form_col4.number_input("Impacto %", min_value=0, max_value=100)
            f8 = form_col6.text_input(
                "Contenção",
                placeholder="Ação provisória",
                help="O que eu fiz para não parar a produção até solucionar o problema",
            )
            f7 = form_col6.text_input(
                "Causa Raiz",
                placeholder="Qual foi a causa raiz",
                help="Qual foi a causa que gerou o problema",
            )
            solucao_help = (  # cspell:disable-line
                "O que eu fiz para eliminar a causa raiz "
                "e o que eu fiz para o problema não ocorrer novamente"
            )
            f9 = form_col6.text_input(
                "Solução",
                placeholder="Ação para eliminar a causa raiz",
                help=solucao_help,  # cspell:disable-line
            )
            feed_help = (
                "Feedback da solução( que informação importante vai ser dada? )"
                " e nome do responsável pelo feedback"
            )
            f10 = form_col7.text_input(
                "Feedback",
                placeholder="Feedback da solução e nome do responsável",
                help=feed_help,
            )
            f11 = form_col8.text_input("Responsável", placeholder="Nome do responsável pela ação")
            f12 = st.checkbox("Conclusão", value=False)

            # Cria um DataFrame com os dados
            df_action_form = pd.DataFrame(
                columns=action_plan_model_df.columns,
                data=[[f1, f2, f3, f4, f13, f5[0], f6, f7, f8, f9, f10, f11, f12]],
            )

            add_action_form_submit = st.form_submit_button("Adicionar")
            if add_action_form_submit:
                save_action(df_action_form)
