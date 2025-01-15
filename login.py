import streamlit as st
from pymongo import MongoClient
from urllib.parse import quote_plus

# Configurar a URI do MongoDB
username = "crm_hygge"
password = "BN1hNGf7cdlRGKL5"
mongo_uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@crmhygge.wiafd.mongodb.net/?retryWrites=true&w=majority&appName=CRMHygge"

# Conectar ao MongoDB
client = MongoClient(mongo_uri)

db = client["crm_database"]  # Nome do banco de dados
collection = db["usuarios"]  # Nome da coleção

# Interface do Streamlit
st.title("Gerenciamento de Usuários")

# Formulário para cadastrar usuários
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
        if nome and email and login and senha:
            # Verificar se já existe um usuário com o mesmo email ou login
            existing_user = collection.find_one({"$or": [{"email": email}, {"login": login}]})
            if existing_user:
                st.error("Usuário já cadastrado com este email ou login!")
            else:
                # Criar documento com os dados
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
            st.error("Por favor, preencha os campos obrigatórios (Nome, Email, Login, Senha).")

# Listar usuários cadastrados
st.header("Usuários Cadastrados")

if st.button("Carregar Usuários"):
    users = list(collection.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
    if users:
        for user in users:
            st.write(user)
    else:
        st.write("Nenhum usuário cadastrado ainda.")

# Formulário para remover usuários
st.header("Remover Usuário")
with st.form("remove_form"):
    remove_email_or_login = st.text_input("Email ou Login do Usuário a Remover", "")
    remove_submit = st.form_submit_button("Remover Usuário")

    if remove_submit:
        if remove_email_or_login:
            # Verificar se o usuário existe
            result = collection.delete_one({"$or": [{"email": remove_email_or_login}, {"login": remove_email_or_login}]})
            if result.deleted_count > 0:
                st.success(f"Usuário com Email/Login '{remove_email_or_login}' removido com sucesso!")
            else:
                st.error(f"Nenhum usuário encontrado com Email/Login '{remove_email_or_login}'.")
        else:
            st.error("Por favor, insira o Email ou Login do usuário para remover.")
