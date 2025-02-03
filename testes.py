import random
from utils.database import get_collection

# Conectar à coleção de empresas
collection_empresas = get_collection("empresas")

# Opções disponíveis
produtos_opcoes = ["NBR Fast", "Consultoria NBR", "Consultoria HYGGE", "Consultoria Certificação"]

# Buscar todas as empresas
empresas = list(collection_empresas.find({}, {"_id": 1}))

# Atualizar cada empresa individualmente com 1 ou 2 produtos aleatórios
for empresa in empresas:
    novos_produtos = random.sample(produtos_opcoes, k=random.randint(1, 2))  # Seleciona 1 ou 2 opções aleatórias
    
    collection_empresas.update_one(
        {"_id": empresa["_id"]},
        {"$set": {"produto_interesse": novos_produtos}}
    )

print("✅ Todas as empresas foram atualizadas com 1 ou 2 opções aleatórias de 'produto_interesse'.")
