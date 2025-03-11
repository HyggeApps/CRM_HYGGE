import streamlit as st
from pymongo import MongoClient # type: ignore
from urllib.parse import quote_plus
import ast

@st.cache_resource
def get_db_client():
    """Retorna o cliente MongoDB usando cache para otimizar conexões."""
    username = "crm_hygge"
    password = "BN1hNGf7cdlRGKL5"
    mongo_uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@crmhygge.wiafd.mongodb.net/?retryWrites=true&w=majority&appName=CRMHygge"
    return MongoClient(mongo_uri)

def get_collection(collection_name):
    """Retorna uma coleção específica do banco de dados."""
    client = get_db_client()  # Usa o cliente cacheado
    db = client["crm_database"]  # Nome do banco de dados
    return db[collection_name]

collection_produtos = get_collection('produtos')

# Iterar por todos os documentos na coleção
for doc in collection_produtos.find({}):
    if "servicos_adicionais" in doc:
        try:
            # Converter a string para dicionário
            servicos = ast.literal_eval(doc["servicos_adicionais"])
            
            # Atualizar os valores conforme solicitado
            if "Reunião" in servicos:
                servicos["Reunião"] = 1500
            if "Urgência" in servicos:
                servicos["Urgência"] = 2000
            if "Cenário extra" in servicos:
                servicos["Cenário extra"] = 1000

            # Converter o dicionário de volta para string ou manter como dicionário, se preferir
            servicos_atualizado = str(servicos)
            
            # Atualizar o documento no banco
            collection_produtos.update_one(
                {"_id": doc["_id"]},
                {"$set": {"servicos_adicionais": servicos_atualizado}}
            )
            print(f"Documento {doc['_id']} atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar documento {doc['_id']}: {e}")