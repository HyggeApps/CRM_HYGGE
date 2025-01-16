import streamlit as st
from utils.database import get_collection
import pandas as pd

def gerenciamento_usuarios():
    st.title("Gerenciamento de Usuários")
    collection = get_collection("usuarios")

    # Aba para cadastrar, remover e exibir usuários
    tab1, tab2, tab3 = st.tabs(["Cadastrar Usuário", "Remover Usuário", "Exibir Usuários"])

    # Aba: Cadastrar Usuário
    with tab1:
        st.header("Cadastrar Usuário")
        with st.form(key="form_cadastro_usuario"):  # Key única para o formulário
            nome = st.text_input("Nome", key="input_nome_usuario")
            sobrenome = st.text_input("Sobrenome", key="input_sobrenome_usuario")
            email = st.text_input("Email", key="input_email_usuario")
            fone = st.text_input("Telefone", key="input_fone_usuario")
            setor = st.text_input("Setor", key="input_setor_usuario")
            login = st.text_input("Login", key="input_login_usuario")
            senha = st.text_input("Senha", type="password", key="input_senha_usuario")
            hierarquia = st.selectbox("Hierarquia", ["Admin", "Usuário", "Gerente", "Outro"], key="input_hierarquia_usuario")

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
        with st.form(key="form_remover_usuario"):  # Key única para o formulário
            remove_email_or_login = st.text_input("Email ou Login do Usuário a Remover", key="input_remover_usuario")
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

    # Aba: Exibir Usuários
    with tab3:
        st.header("Usuários Cadastrados")
        if st.button("Carregar Usuários", key="botao_carregar_usuarios"):  # Key única para o botão
            users = list(collection.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if users:
                # Converter a lista de usuários em um DataFrame para exibição tabular
                df_users = pd.DataFrame(users)
                st.dataframe(df_users)  # Exibir como tabela
            else:
                st.write("Nenhum usuário cadastrado ainda.")
