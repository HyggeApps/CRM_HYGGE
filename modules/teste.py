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

# Primeiro: remove o campo "escopo" dos produtos da categoria MCMV
resultado_unset = collection_produtos.update_many(
    {"categoria": "MCMV"},
    {"$unset": {"escopo": ""}}
)
print("Campo 'escopo' removido de", resultado_unset.modified_count, "documentos.")

# Em seguida: define a lista de escopo corrigida
escopo_list = [
    'Laudo Normativo por simulação computacional para o desempenho Térmico da NBR 15.575:2024',
    'Laudo Normativo por simulação computacional para o desempenho Lumínico Natural da NBR 15.575:2024',
    'Análise por simulação computacional dos itens 2.2 e 2.3 do Selo Casa Azul + CAIXA',
    'Modelo 3D com os resultados obtidos por simulação computacional'
]

# Atualiza os documentos com a lista corrigida
resultado_set = collection_produtos.update_many(
    {"categoria": "MCMV"},
    {"$set": {"escopo": escopo_list}}
)
print("Campo 'escopo' atualizado em", resultado_set.modified_count, "documentos.")