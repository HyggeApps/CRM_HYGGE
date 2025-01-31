import random
from faker import Faker
from datetime import datetime, timedelta
from utils.database import get_collection

fake = Faker("pt_BR")

def gerar_cnpj_falso():
    """Gera um CNPJ válido e aleatório"""
    def calcular_digito(cnpj_parcial):
        """Calcula os dois dígitos verificadores de um CNPJ"""
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6] + pesos1

        soma1 = sum(int(cnpj_parcial[i]) * pesos1[i] for i in range(12))
        digito1 = 11 - soma1 % 11 if soma1 % 11 >= 2 else 0

        soma2 = sum(int(cnpj_parcial[i]) * pesos2[i] for i in range(12)) + digito1 * pesos2[12]
        digito2 = 11 - soma2 % 11 if soma2 % 11 >= 2 else 0

        return str(digito1) + str(digito2)

    base = f"{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(100, 999)}0001"
    return base + calcular_digito(base)

def cadastrar_empresas_ficticias(qtd=1500):
    """Cadastra empresas fictícias e cria tarefas associadas"""
    collection_empresas = get_collection("empresas")
    collection_tarefas = get_collection("tarefas")

    setores = ["Comercial", "Residencial", "Residencial MCMV", "Industrial"]
    produtos = ["NBR Fast", "Consultoria NBR", "Consultoria HYGGE", "Consultoria Certificação"]
    tamanhos = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]
    graus = ["Lead", "Lead Qualificado", "Oportunidade", "Cliente"]
    usuarios_ficticios = [fake.first_name() for _ in range(50)]  # Criar 50 usuários fictícios

    empresas = []
    tarefas = []
    data_atual = datetime.today().strftime("%Y-%m-%d")

    for _ in range(qtd):
        cnpj = gerar_cnpj_falso()

        empresa = {
            "razao_social": fake.company(),
            "cnpj": cnpj,
            "cidade": fake.city(),
            "estado": fake.state_abbr(),
            "setor": random.choice(setores),
            "tamanho_empresa": random.choice(tamanhos),
            "produto_interesse": random.choice(produtos),
            "grau_cliente": random.choice(graus),
            "usuario": random.choice(usuarios_ficticios),
            "data_criacao": data_atual,
            "ultima_atividade": data_atual,
        }
        empresas.append(empresa)

        tarefa = {
            "titulo": "Identificar personas",
            "empresa": cnpj,
            "data_execucao": (datetime.today().date() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "observacoes": "Nova empresa cadastrada",
            "status": "🟨 Em andamento"
        }
        tarefas.append(tarefa)

    # Inserir todas as empresas e tarefas no banco
    collection_empresas.insert_many(empresas)
    collection_tarefas.insert_many(tarefas)

    print(f"✅ {qtd} empresas fictícias cadastradas com sucesso!")

# Executar o script para cadastrar 1.500 empresas
cadastrar_empresas_ficticias(1500)