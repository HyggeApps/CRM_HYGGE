from utils.database import get_collection
from datetime import datetime, timedelta
import random

def gerar_atividades_teste(empresa_cnpj):
    collection_atividades = get_collection("atividades")

    tipos_atividade = ["Whatsapp", "Ligação", "Email", "Linkedin", "Reunião"]
    status_atividade = ["NA", "Ocupado", "Conectado", "Gatekeeper", "Ligação Positiva", "Ligação Negativa"]
    titulos = ["Contato com cliente", "Apresentação de proposta", "Follow-up", "Reunião de alinhamento", "Negociação"]
    descricoes = ["Discutimos a proposta inicial.", "Cliente solicitou ajustes no contrato.", 
                  "Marcação de reunião para próxima semana.", "Cliente interessado no produto.", 
                  "Necessário novo contato após 15 dias."]

    # Criar atividades distribuídas pelos últimos 12 meses
    for i in range(20):
        meses_atras = random.randint(0, 30)  # Escolhe um mês dentro do último ano
        data_execucao = datetime.today() - timedelta(days=meses_atras * 30 + random.randint(1, 28))

        atividade_id = str(datetime.now().timestamp())  # ID único baseado no tempo
        nova_atividade = {
            "atividade_id": atividade_id,
            "tipo_atividade": random.choice(tipos_atividade),
            "status": random.choice(status_atividade),
            "titulo": random.choice(titulos),
            "empresa": empresa_cnpj,
            "contato": ["Contato Teste (contato@teste.com)"],  # Contato fictício
            "descricao": random.choice(descricoes),
            "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
            "data_criacao_atividade": datetime.now().strftime("%Y-%m-%d")
        }

        collection_atividades.insert_one(nova_atividade)

    print("✅ 20 atividades de teste foram inseridas no banco de dados!")

# Chamando a função com um CNPJ de exemplo
gerar_atividades_teste("03214866000193")