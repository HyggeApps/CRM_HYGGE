from urllib.parse import quote_plus
from pymongo import MongoClient

# Configurar a URI do MongoDB
username = "crm_hygge"
password = "BN1hNGf7cdlRGKL5"
mongo_uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@crmhygge.wiafd.mongodb.net/?retryWrites=true&w=majority&appName=CRMHygge"

# Conectar ao MongoDB
try:
    client = MongoClient(mongo_uri)
    print("Conexão estabelecida com sucesso.")

    # Listar todos os bancos de dados
    databases = client.list_database_names()
    print("\nBancos de dados disponíveis:")
    for db_name in databases:
        print(f" - {db_name}")
        
        # Listar todas as coleções de cada banco de dados
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"   Coleções em {db_name}:")
        for collection_name in collections:
            print(f"     - {collection_name}")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
finally:
    client.close()
