import ast
from pymongo import MongoClient
from urllib.parse import quote_plus

def get_db_client():
    username = "crm_hygge"
    password = "BN1hNGf7cdlRGKL5"
    mongo_uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@crmhygge.wiafd.mongodb.net/?retryWrites=true&w=majority&appName=CRMHygge"
    return MongoClient(mongo_uri)

def get_collection(collection_name):
    client = get_db_client()
    db = client["crm_database"]
    return db[collection_name]

# Conecta à coleção "produtos"
collection_produtos = get_collection("produtos")

# Primeiro: remove o campo "escopo" dos produtos da categoria Consultoria
resultado_unset = collection_produtos.update_many(
    {
        "categoria": "Consultoria",
        "tipo": {"$regex": "NBR"}
    },
    {"$unset": {"escopo": ""}}
)
print("Campo 'escopo' removido de", resultado_unset.modified_count, "documentos.")

# Define a lista de escopo corrigida
escopo_list = [
    'Laudo diagnóstico para NBR 15.575 por simulação computacional para o térmico e lumínico natural.'
]

# Atualiza os documentos que não possuem o campo "escopo", adicionando-o com escopo_list
resultado_set = collection_produtos.update_many(
    {
        "categoria": "Consultoria",
        "tipo": {"$regex": "NBR"},
        "escopo": {"$exists": False}
    },
    {"$set": {"escopo": escopo_list}}
)
print("Campo 'escopo' atualizado em", resultado_set.modified_count, "documentos.")
