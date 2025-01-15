import streamlit as st
from utils.database import get_collection

def cadastro_usuarios():
    st.title("Cadastro de Usuários")
    collection = get_collection("usuarios")

    with st.form("user_form"):
        nome = st.text_input("Nome", "")
        email = st.text_input("Email", "")
        login = st.text_input("Login", "")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Cadastrar")

        if submit:
            if nome and email and login and senha:
                existing_user = collection.find_one({"$or": [{"email": email}, {"login": login}]})
                if existing_user:
                    st.error("Usuário já cadastrado com este email ou login!")
                else:
                    document = {"nome": nome, "email": email, "login": login, "senha": senha}
                    collection.insert_one(document)
                    st.success("Usuário cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos obrigatórios.")
