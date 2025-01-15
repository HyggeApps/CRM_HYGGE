import streamlit as st
from utils.database import get_collection

def cadastro_usuarios():
    st.title("Gerenciamento de Usuários")
    collection = get_collection("usuarios")

    # Aba para cadastrar e remover usuários
    tab1, tab2 = st.tabs(["Cadastrar Usuário", "Remover Usuário"])

    # Aba: Cadastrar Usuário
    with tab1:
        st.header("Cadastrar Usuário")
        with st.form("user_form"):
            nome = st.text_input("Nome", "")
            sobrenome = st.text_input("Sobrenome", "")
            email = st.text_input("Email", "")
            fone = st.text_input("Telefone", "")
            setor = st.text_input("Setor", "")
            login = st.text_input("Login", "")
            senha = st.text_input("Senha", type="password")
            hierarquia = st.selectbox("Hierarquia", ["Admin", "Usuário", "Gerente", "Outro"])

            submit = st.form_submit_button("Cadastrar")

            if submit:
                if nome and sobrenome and email and login and senha:
                    # Verificar duplicidade no banco de dados
                    existing_user = collection.find_one({"$or": [{"email": email}, {"login": login}]})
                    if existing_user:
                        st.error("Usuário já cadastrado com este email ou login!")
                    else:
                        # Criar o documento
                        document = {
                            "nome": nome,
                            "sobrenome": sobrenome,
                            "email": email,
                            "fone": fone,
                            "setor": setor,
                            "login": login,
                            "senha": senha,
                            "hierarquia": hierarquia,
                        }
                        collection.insert_one(document)
                        st.success("Usuário cadastrado com sucesso!")
                else:
                    st.error("Preencha todos os campos obrigatórios (Nome, Sobrenome, Email, Login, Senha).")

    # Aba: Remover Usuário
    with tab2:
        st.header("Remover Usuário")
        with st.form("remove_form"):
            remove_email_or_login = st.text_input("Email ou Login do Usuário a Remover", "")
            remove_submit = st.form_submit_button("Remover Usuário")

            if remove_submit:
                if remove_email_or_login:
                    # Verificar se o usuário existe e remover
                    result = collection.delete_one({"$or": [{"email": remove_email_or_login}, {"login": remove_email_or_login}]})
                    if result.deleted_count > 0:
                        st.success(f"Usuário com Email/Login '{remove_email_or_login}' removido com sucesso!")
                    else:
                        st.error(f"Nenhum usuário encontrado com Email/Login '{remove_email_or_login}'.")
                else:
                    st.error("Por favor, insira o Email ou Login do usuário para remover.")