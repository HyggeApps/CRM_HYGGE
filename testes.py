import random
from faker import Faker
from datetime import datetime, timedelta
from utils.database import get_collection

fake = Faker("pt_BR")

def gerar_cnpj_falso():
    """Gera um CNPJ válido e aleatório"""
    def calcular_digito(cnpj_parcial):
        """Calcula os dígitos verificadores do CNPJ"""
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6] + pesos1

        soma1 = sum(int(cnpj_parcial[i]) * pesos1[i] for i in range(12))
        digito1 = 11 - soma1 % 11 if soma1 % 11 >= 2 else 0

        soma2 = sum(int(cnpj_parcial[i]) * pesos2[i] for i in range(12)) + digito1 * pesos2[12]
        digito2 = 11 - soma2 % 11 if soma2 % 11 >= 2 else 0

        return str(digito1) + str(digito2)

    base = f"{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(100, 999)}0001"
    return base + calcular_digito(base)


def cadastrar_empresas(qtd=1500):
    """Cadastra empresas fictícias"""
    collection_empresas = get_collection("empresas")

    setores = ["Comercial", "Residencial", "Residencial MCMV", "Industrial"]
    produtos = ["NBR Fast", "Consultoria NBR", "Consultoria HYGGE", "Consultoria Certificação"]
    tamanhos = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]
    graus = ["Lead", "Lead Qualificado", "Oportunidade", "Cliente"]
    usuarios_ficticios = [fake.first_name() for _ in range(50)]

    empresas = []
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

    collection_empresas.insert_many(empresas)
    print(f"✅ {qtd} empresas fictícias cadastradas com sucesso!")
    return empresas


def cadastrar_contatos(empresas):
    """Gera de 0 a 5 contatos para cada empresa"""
    collection_contatos = get_collection("contatos")

    contatos = []
    cargos_possiveis = ["CEO", "Diretor Comercial", "Gerente de Projetos", "Analista de Vendas", "Consultor Técnico"]

    for empresa in empresas:
        cnpj = empresa["cnpj"]
        num_contatos = random.randint(0, 5)

        for _ in range(num_contatos):
            nome = fake.first_name()
            sobrenome = fake.last_name()
            email = f"{nome.lower()}.{sobrenome.lower()}@{fake.domain_name()}"
            telefone = fake.phone_number()
            cargo = random.choice(cargos_possiveis)

            contato = {
                "nome": nome,
                "sobrenome": sobrenome,
                "cargo": cargo,
                "email": email,
                "fone": telefone,
                "empresa": cnpj
            }
            contatos.append(contato)

    if contatos:
        collection_contatos.insert_many(contatos)
        print(f"✅ {len(contatos)} contatos fictícios cadastrados com sucesso!")
    else:
        print("⚠️ Nenhum contato gerado.")


def cadastrar_tarefas(empresas):
    """Cria de 5 a 10 tarefas por empresa com diferentes estágios"""
    collection_tarefas = get_collection("tarefas")

    status_possiveis = ["🟨 Em andamento", "🟥 Atrasado", "🟩 Concluída"]
    tarefas = []

    for empresa in empresas:
        cnpj = empresa["cnpj"]
        num_tarefas = random.randint(5, 10)

        for _ in range(num_tarefas):
            data_execucao = datetime.today().date() - timedelta(days=random.randint(-30, 30))
            status = random.choices(status_possiveis, weights=[50, 30, 20])[0]

            tarefa = {
                "titulo": f"Tarefa {fake.word().capitalize()}",
                "empresa": cnpj,
                "data_execucao": data_execucao.strftime("%Y-%m-%d"),
                "observacoes": fake.sentence(),
                "status": status
            }
            tarefas.append(tarefa)

    collection_tarefas.insert_many(tarefas)
    print(f"✅ {len(tarefas)} tarefas fictícias cadastradas com sucesso!")


def cadastrar_atividades(empresas):
    """Cria de 20 a 30 atividades por empresa, com datas variadas"""
    collection_atividades = get_collection("atividades")

    tipos_atividades = ["Whatsapp", "Ligação", "Email", "Linkedin", "Reunião", "Observação"]
    atividades = []

    for empresa in empresas:
        cnpj = empresa["cnpj"]
        num_atividades = random.randint(20, 30)

        for _ in range(num_atividades):
            dias_passados = random.randint(-60, 0)
            data_execucao = datetime.today().date() + timedelta(days=dias_passados)

            atividade = {
                "atividade_id": str(datetime.now().timestamp()),
                "tipo_atividade": random.choice(tipos_atividades),
                "status": "Registrado",
                "titulo": f"Atividade {fake.word().capitalize()}",
                "empresa": cnpj,
                "descricao": fake.sentence(),
                "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
                "data_criacao_atividade": datetime.today().strftime("%Y-%m-%d")
            }
            atividades.append(atividade)

    collection_atividades.insert_many(atividades)
    print(f"✅ {len(atividades)} atividades fictícias cadastradas com sucesso!")


# 🚀 **Rodando o script completo**
print("🔄 Iniciando a geração de dados fictícios para o CRM...")

# 1️⃣ Criar empresas
empresas_cadastradas = cadastrar_empresas(1500)

# 2️⃣ Criar contatos para as empresas
cadastrar_contatos(empresas_cadastradas)

# 3️⃣ Criar tarefas para as empresas
cadastrar_tarefas(empresas_cadastradas)

# 4️⃣ Criar atividades para as empresas
cadastrar_atividades(empresas_cadastradas)

print("🎉 Dados fictícios gerados com sucesso!")
