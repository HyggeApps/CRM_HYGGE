import streamlit as st
from utils.database import get_collection
import pandas as pd

def gerenciamento_usuarios():
    collection = get_collection("usuarios")
    st.info("Cadastre, remova ou liste os usuários a partir das opções abaixo.")
    # Aba para cadastrar, remover e exibir usuários
    tab1, tab2, tab3 = st.tabs(["Cadastrar Usuário", "Remover Usuário", "Exibir Usuários"])

    # Aba: Cadastrar Usuário
    with tab1:
        st.subheader("Cadastrar Usuário")
        with st.form(key="form_cadastro_usuario"):  # Key única para o formulário
            nome = st.text_input("Nome", key="input_nome_usuario")
            sobrenome = st.text_input("Sobrenome", key="input_sobrenome_usuario")
            email = st.text_input("Email", key="input_email_usuario")
            fone = st.text_input("Telefone", key="input_fone_usuario")
            setor = st.text_input("Setor", key="input_setor_usuario")
            login = st.text_input("Login", key="input_login_usuario")
            senha = st.text_input("Senha", type="password", key="input_senha_usuario")
            hierarquia = st.selectbox("Hierarquia", ["admin", "viewer", "editor"], key="input_hierarquia_usuario")

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
        st.subheader("Remover Usuário")

        # Obter todos os usuários cadastrados
        users = list(collection.find({}, {"_id": 0, "email": 1, "login": 1}))  # Buscar apenas email e login
        opcoes_usuarios = [f"{user['email']} ({user['login']})" for user in users]  # Combinar email e login

        if not opcoes_usuarios:
            st.warning("Nenhum usuário encontrado. Cadastre usuários antes de tentar removê-los.")
        else:
            with st.form(key="form_remover_usuario"):  # Key única para o formulário
                # Lista suspensa com os emails/logins dos usuários
                usuario_selecionado = st.selectbox("Selecione o Usuário a Remover", options=opcoes_usuarios, key="select_remover_usuario")
                remove_submit = st.form_submit_button("Remover Usuário")

                if remove_submit:
                    if usuario_selecionado:
                        # Extrair o email do usuário selecionado
                        email = usuario_selecionado.split(" ")[0]  # Extrair o primeiro elemento (email)
                        result = collection.delete_one({"email": email})
                        if result.deleted_count > 0:
                            st.success(f"Usuário com Email '{email}' removido com sucesso!")
                        else:
                            st.error(f"Nenhum usuário encontrado com o Email '{email}'.")

    # Aba: Exibir Usuários
    with tab3:
        st.subheader("Usuários Cadastrados")
        if st.button("Carregar Usuários", key="botao_carregar_usuarios"):  # Key única para o botão
            users = list(collection.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if users:
                # Converter a lista de usuários em um DataFrame
                import pandas as pd
                df_users = pd.DataFrame(users)

                # Remover a coluna 'senha' para não ser exibida
                if 'senha' in df_users.columns:
                    df_users = df_users.drop(columns=['senha'])

                # Exibir a tabela em tela cheia
                st.dataframe(
                    df_users,
                    use_container_width=True  # Ocupa a largura total da tela
                )
            else:
                st.write("Nenhum usuário cadastrado ainda.")

