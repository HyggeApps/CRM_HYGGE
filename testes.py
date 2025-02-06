import random
from datetime import datetime, timedelta
from utils.database import get_collection

# Conectar à coleção de tarefas
collection_tarefas = get_collection("tarefas")

# Filtrar tarefas atrasadas
tarefas_atrasadas = list(collection_tarefas.find({"status": "🟥 Atrasado"}, {"_id": 1, "data_execucao": 1}))

# Gerar uma nova data aleatória em 2024
def gerar_data_aleatoria_2024():
    data_inicio = datetime(2024, 1, 1)
    data_fim = datetime(2024, 12, 31)
    diferenca = (data_fim - data_inicio).days
    return (data_inicio + timedelta(days=random.randint(0, diferenca))).strftime("%Y-%m-%d")

# Atualizar cada tarefa atrasada
for tarefa in tarefas_atrasadas:
    nova_data_execucao = gerar_data_aleatoria_2024()
    
    collection_tarefas.update_one(
        {"_id": tarefa["_id"]},
        {"$set": {"data_execucao": nova_data_execucao}}
    )

print(f"✅ {len(tarefas_atrasadas)} tarefas atrasadas foram atualizadas para datas aleatórias de 2024.")
