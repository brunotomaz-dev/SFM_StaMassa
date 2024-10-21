""" Módulo para plano d e ação """

import pandas as pd
import streamlit as st


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

    st.session_state.table_action = pd.concat(
        [st.session_state.table_action, df], ignore_index=True
    )
    add_action_form()
    st.rerun()


def add_action_form() -> None:
    """Toggle de edição da tabela de plano de ação."""
    st.session_state.add_action = not st.session_state.add_action


def handle_added_rows(alt_table: pd.DataFrame) -> None:
    """Adiciona as linhas adicionadas na edição da tabela de plano de ação.

    Essa função pega as linhas que foram adicionadas na edição da tabela e
    as concatena com a tabela original de plano de ação.

    Args:
        alt_table (pd.DataFrame): A tabela editada com as linhas adicionadas.
    """
    if len(alt_table["added_rows"]) > 0:
        print(alt_table["added_rows"])
        st.session_state.table_action = pd.concat(
            [st.session_state.table_action, pd.DataFrame(alt_table["added_rows"])],
            ignore_index=True,
        )


def handle_deleted_rows(alt_table: pd.DataFrame) -> None:
    """Remove as linhas excluídas na edição da tabela de plano de ação.

    Essa função pega as linhas que foram excluídas na edição da tabela e
    as remove da tabela original de plano de ação.
    """
    if len(alt_table["deleted_rows"]) > 0:
        print(alt_table["deleted_rows"])
        st.session_state.table_action = st.session_state.table_action.drop(
            alt_table["deleted_rows"], axis=0
        )


def handle_edited_rows(alt_table: pd.DataFrame) -> None:
    """Salva as alterações feitas na edição da tabela de plano de ação.

    Essa função pega as alterações feitas na edição da tabela e as aplica na
    tabela original de plano de ação.
    """
    if len(alt_table["edited_rows"]) > 0:
        keys = list(alt_table["edited_rows"].keys())
        values = list(alt_table["edited_rows"].values())
        for str_idx, changes in alt_table["edited_rows"].items():
            idx = int(str_idx)
            for col, new_value in changes.items():
                st.session_state.table_action.at[idx, col] = new_value


def session_state_start() -> None:
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

    if "table_action" not in st.session_state:
        st.session_state.table_action = pd.DataFrame(
            columns=[
                "Data",
                "Indicador",
                "Dias em Aberto",
                "Prioridade",
                "Descrição do Problema",
                "Impacto %",
                "Causa Raiz",
                "Contenção",
                "Solução",
                "Feedback",
                "Responsável",
                "Conclusão",
            ],
        )


# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #


def action_plan() -> None:
    """Plano de ação."""
    session_state_start()

    # Tabela
    df_action = st.session_state.table_action

    # Tabela
    if st.session_state.edit_action:
        config = {
            "Data": st.column_config.DateColumn(format="DD/MM/YYYY", default=pd.Timestamp("today")),
            "Indicador": st.column_config.SelectboxColumn(options=["S", "Q", "D", "C"]),
            "Dias em Aberto": st.column_config.NumberColumn(),
            "Prioridade": st.column_config.SelectboxColumn(options=[1, 2, 3]),
            "Descrição do Problema": st.column_config.TextColumn(),
            "Impacto %": st.column_config.NumberColumn(format="%.2f%%", min_value=0, max_value=100),
            "Causa Raiz": st.column_config.TextColumn(),
            "Contenção": st.column_config.TextColumn(),
            "Solução": st.column_config.TextColumn(),
            "Feedback": st.column_config.TextColumn(),
            "Responsável": st.column_config.TextColumn(),
            "Conclusão": st.column_config.CheckboxColumn(default=False),
        }
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
        df_action_filtered = df_action[df_action["Conclusão"] == 0]
        # Configuração da coluna "Impacto %"
        config = {
            "Impacto %": st.column_config.NumberColumn(
                format="%.0f%%",  # Formato de porcentagem
                help="Impacto em porcentagem",
            )
        }
        st.dataframe(
            df_action_filtered, use_container_width=True, column_config=config, hide_index=True
        )

    # Botões
    with st.sidebar:
        st.subheader("Tabela de Ações")
        side_col, side_col_2 = st.columns(2)
        side_col.button("Editar", on_click=edit_action, use_container_width=True)
        side_col_2.button("Adicionar", on_click=add_action_form, use_container_width=True)

    if st.session_state.add_action:
        with st.form(key="form_add_action", clear_on_submit=True):
            st.write("Plano de ação - Adicionar")
            form_col1, form_col2, form_col3, form_col4 = st.columns(4)
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
            f5 = form_col5.text_area("Descrição do Problema", height=207)
            f6 = form_col4.number_input("Impacto %", min_value=0, max_value=100)
            f7 = form_col6.text_input("Causa Raiz")
            f8 = form_col6.text_input("Contenção")
            f9 = form_col6.text_input("Solução")
            f10 = form_col7.text_input("Feedback")
            f11 = form_col8.text_input("Responsável")
            f12 = st.checkbox("Conclusão", value=False)

            # Cria um DataFrame com os dados
            df_action_form = pd.DataFrame(
                {
                    "Data": [f1],
                    "Indicador": [f2],
                    "Dias em Aberto": [f3],
                    "Prioridade": [f4],
                    "Descrição do Problema": [f5],
                    "Impacto %": [f6],
                    "Causa Raiz": [f7],
                    "Contenção": [f8],
                    "Solução": [f9],
                    "Feedback": [f10],
                    "Responsável": [f11],
                    "Conclusão": [f12],
                }
            )
            add_action_form_submit = st.form_submit_button("Adicionar")
            if add_action_form_submit:
                save_action(df_action_form)
