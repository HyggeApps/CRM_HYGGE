import random
from faker import Faker
from utils.database import get_collection

fake = Faker("pt_BR")

def cadastrar_contatos_ficticios():
    """Gera de 0 a 5 contatos para cada empresa já cadastrada"""
    collection_empresas = get_collection("empresas")
    collection_contatos = get_collection("contatos")

    # Buscar todas as empresas cadastradas
    empresas = list(collection_empresas.find({}, {"_id": 0, "cnpj": 1, "razao_social": 1}))

    contatos = []
    cargos_possiveis = ["CEO", "Diretor Comercial", "Gerente de Projetos", "Analista de Vendas", "Consultor Técnico"]

    for empresa in empresas:
        cnpj = empresa["cnpj"]
        num_contatos = random.randint(0, 5)  # Define entre 0 e 5 contatos por empresa

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
                "empresa": cnpj  # Vincula contato ao CNPJ da empresa
            }
            contatos.append(contato)

    if contatos:
        collection_contatos.insert_many(contatos)
        print(f"✅ {len(contatos)} contatos fictícios cadastrados com sucesso!")
    else:
        print("⚠️ Nenhum contato foi gerado.")

# Executar o script para cadastrar contatos fictícios
cadastrar_contatos_ficticios()
