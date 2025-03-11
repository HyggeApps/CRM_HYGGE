from pymongo import MongoClient
from urllib.parse import quote_plus
import streamlit as st

def get_db_client():
    username = "crm_hygge"
    password = "BN1hNGf7cdlRGKL5"
    mongo_uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@crmhygge.wiafd.mongodb.net/?retryWrites=true&w=majority&appName=CRMHygge"
    return MongoClient(mongo_uri)

def get_collection(collection_name):
    client = get_db_client()
    db = client["crm_database"]
    return db[collection_name]

# Define as combinações para cada categoria
# Valores para "NBR Fast" (torres ou casas) e para os outros (áreas em m²)
tamanhos_torres = ['Até 6 Torres', '7 a 12 Torres', '13 a 18 Torres', '19 a 24 Torres', '25 a 35 Torres', '42 Torres ou mais']
tamanhos_casas = ['Até 50 Casas', '51 a 100 Casas', '101 a 150 Casas', '151 a 200 Casas', '201 a 250 Casas', '350 Casas ou mais']
tamanhos_area = ['1 mil m²', '3 mil m²', '5 mil m²', '10 mil m²', '15 mil m²', '20 mil m²']

# Categoria: MCMV
mcmv_types = {
    "NBR Fast - Prédios": tamanhos_torres,
    "NBR Fast - Casas": tamanhos_casas,
    "NBR Fast Economy": tamanhos_torres,
    "Aditivo de NBR - Prédios": tamanhos_torres,
    "Aditivo de NBR - Casas": tamanhos_casas 
}

# Categoria: Consultoria
consultoria_types = {
    # Para os tipos onde o tamanho é medido em área:
    "NBR Médio Padrão - 1 tipo": tamanhos_area,
    "NBR Médio Padrão - Até 3 tipos": tamanhos_area,
    "NBR Alto Padrão - 3 tipos + Duplex": tamanhos_area,
    "NBR Altíssimo Padrão - +5 tipos": tamanhos_area,
    "Consultoria HYGGE Residencial - Médio Padrão": tamanhos_area,
    "Consultoria HYGGE Residencial - Alto Padrão": tamanhos_area,
    "Consultoria HYGGE Residencial - Altíssimo Padrão": tamanhos_area,
}

# Categoria: Certificação
certificacao_types = {
    "EVTA Certificação - Residencial EDGE Médio Padrão": tamanhos_area,
    "EVTA Certificação - Residencial EDGE Alto Padrão": tamanhos_area,
    "EVTA Certificação - Residencial EDGE Altíssimo Padrão": tamanhos_area,
    "EVTA Certificação - Comercial EDGE Médio Padrão": tamanhos_area,
    "EVTA Certificação - Comercial EDGE Alto Padrão": tamanhos_area,
    "EVTA Certificação - Comercial EDGE Altíssimo Padrão": tamanhos_area,
    "Certificação - Residencial EDGE Médio Padrão": tamanhos_area,
    "Certificação - Residencial EDGE Alto Padrão": tamanhos_area,
    "Certificação - Residencial EDGE Altíssimo Padrão": tamanhos_area,
    "Certificação - Comercial EDGE Médio Padrão": tamanhos_area,
    "Certificação - Comercial EDGE Alto Padrão": tamanhos_area,
    "Certificação - Comercial EDGE Altíssimo Padrão": tamanhos_area,
    "Certificação - Residencial Fitwell Médio Padrão": tamanhos_area,
    "Certificação - Residencial Fitwell Alto Padrão": tamanhos_area,
    "Certificação - Residencial Fitwell Altíssimo Padrão": tamanhos_area,
}

auditoria_types = {
    "Auditoria Certificação - Residencial EDGE Médio Padrão": tamanhos_area,
    "Auditoria Certificação - Residencial EDGE Alto Padrão": tamanhos_area,
    "Auditoria Certificação - Residencial EDGE Altíssimo Padrão": tamanhos_area,
}

# Junta todas as combinações em um dicionário
categorias = {
    "MCMV": mcmv_types,
    "Consultoria": consultoria_types,
    "Certificação": certificacao_types,
    "Auditoria": auditoria_types,
}

# Valores fictícios para os preços (você pode editar estes valores posteriormente no banco)
preco_modelagem_default = 150.0
preco_servico_default = 200.0

# Conecta à coleção "produtos"
collection_produtos = get_collection("produtos")

# (Opcional) Limpa a coleção para recriar o banco de produtos
collection_produtos.drop()

# Lista para armazenar os documentos a serem inseridos
produtos_docs = []

# Itera em cada categoria e suas combinações
for categoria, tipos in categorias.items():
    for tipo, tamanhos in tipos.items():
        for tamanho in tamanhos:
            produto = {
                "nome": f'{tipo} - {tamanho}',
                "categoria": categoria,
                "tipo": tipo,
                "tamanho": tamanho,
                "preco_modelagem": preco_modelagem_default,
                "preco_servico": preco_servico_default,
                "servicos_adicionais": {'Reunião':1000, 'Urgência':2000, 'Cenário extra':2500}
            }
            produtos_docs.append(produto)

# Insere todos os produtos na coleção
if produtos_docs:
    result = collection_produtos.insert_many(produtos_docs)
    st.success(f"Inseridos {len(result.inserted_ids)} documentos na coleção 'produtos'.")
else:
    st.error("Nenhum produto gerado.")
