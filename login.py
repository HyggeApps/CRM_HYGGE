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
st.title("Cadastro de Usuários")

# Formulário para cadastrar usuários
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
        if usuario_id and nome and email and login and senha:
            # Criar documento com os dados
            document = {
                "usuario_id": usuario_id,
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
            st.error("Por favor, preencha os campos obrigatórios (ID, Nome, Email, Login, Senha).")

# Listar usuários cadastrados
st.header("Usuários Cadastrados")

if st.button("Carregar Usuários"):
    users = list(collection.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
    if users:
        for user in users:
            st.write(user)
    else:
        st.write("Nenhum usuário cadastrado ainda.")
