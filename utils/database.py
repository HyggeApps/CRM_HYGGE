from pymongo import MongoClient
from urllib.parse import quote_plus

def get_collection(collection_name):
    username = "crm_hygge"
    password = "BN1hNGf7cdlRGKL5"
    mongo_uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@crmhygge.wiafd.mongodb.net/?retryWrites=true&w=majority&appName=CRMHygge"

    client = MongoClient(mongo_uri)
    db = client["crm_database"]
    return db[collection_name]