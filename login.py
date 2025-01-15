import streamlit as st
from pymongo import MongoClient
from urllib.parse import quote_plus

# Configurar a URI do MongoDB
username = "crm_hygge"
password = "BN1hNGf7cdlRGKL5"
mongo_uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@crmhygge.wiafd.mongodb.net/?retryWrites=true&w=majority&appName=CRMHygge"

# Conectar ao MongoDB
client = MongoClient(mongo_uri)

db = client["test_database"]  # Nome do banco de dados
collection = db["test_collection"]  # Nome da coleção


# Adicionar um documento à coleção
st.header("Adicionar Documento")

name = st.text_input("Nome", "")
age = st.number_input("Idade", min_value=0, max_value=120, step=1, value=18)
submit = st.button("Adicionar")

if submit:
    if name:
        # Criar um documento para adicionar
        document = {"name": name, "age": age}
        collection.insert_one(document)
        st.success(f"Documento adicionado: {document}")
    else:
        st.error("Por favor, insira um nome.")

# Listar documentos na coleção
st.header("Documentos na Coleção")

if st.button("Carregar Documentos"):
    documents = list(collection.find())
    if documents:
        for doc in documents:
            st.write(doc)
    else:
        st.write("Nenhum documento encontrado.")