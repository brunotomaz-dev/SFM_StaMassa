import streamlit as st

if st.session_state["authentication_status"]:
    st.title(f"Seja Bem vindo {st.session_state['name']}")

    if st.session_state["role"] == "dev":
        st.subheader("Desenvolvedor")
        st.sidebar.write("Opções:")
        add_user =st.sidebar.button("Adicionar Usuário")

        if add_user:
            st.session_state["add_user"] = 1 if st.session_state["add_user"] == 0 else 0
            st.rerun()

    pass_reset = st.sidebar.button("Alterar Senha")
    if pass_reset:
        st.session_state["pass_reset"] = 1 if st.session_state["pass_reset"] == 0 else 0
        st.rerun()