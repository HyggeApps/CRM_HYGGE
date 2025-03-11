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

# Busca os documentos onde servicos_adicionais está armazenado como string
cursor = collection_produtos.find({"servicos_adicionais": {"$type": "string"}})

for doc in cursor:
    servicos_str = doc.get("servicos_adicionais")
    try:
        # Converte a string para dicionário
        servicos = ast.literal_eval(servicos_str)
        # Verifica e atualiza a chave, se presente
        if "Cenário extra" in servicos:
            valor = servicos.pop("Cenário extra")
            servicos["Cenário adicional"] = valor

            # Atualiza o documento, armazenando servicos_adicionais como dicionário
            result = collection_produtos.update_one(
                {"_id": doc["_id"]},
                {"$set": {"servicos_adicionais": servicos}}
            )
            print(f"Documento {doc['_id']} atualizado com sucesso.")
    except Exception as e:
        print(f"Erro ao converter servicos_adicionais no documento {doc['_id']}: {e}")
