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
# Verifica se há documentos na coleção
if collection.count_documents({}) == 0:
    st.info("A coleção está vazia. Adicionando um documento inicial...")
    collection.insert_one({"message": "Initial document"})
