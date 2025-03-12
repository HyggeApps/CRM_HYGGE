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

query = {"servicos_adicionais.Cenário adicional": {"$exists": True}}
cursor = collection_produtos.find(query)
count_updated = 0

for doc in cursor:
    servicos = doc.get("servicos_adicionais", {})
    if isinstance(servicos, dict) and "Cenário adicional" in servicos:
        valor = servicos["Cenário adicional"]
        # Remove a chave antiga e adiciona a nova
        del servicos["Cenário adicional"]
        servicos["Cenário adicional de simulação"] = valor
        
        collection_produtos.update_one(
            {"_id": doc["_id"]},
            {"$set": {"servicos_adicionais": servicos}}
        )
        count_updated += 1

print(f"Documentos atualizados: {count_updated}")