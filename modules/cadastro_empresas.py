import streamlit as st
import requests
from utils.database import get_collection

def buscar_dados_cnpj(cnpj):
    """Busca dados de uma empresa pelo CNPJ usando a API CNPJ.ws ou outra alternativa."""
    url = f"https://www.cnpj.ws/api/v1/cnpj/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def buscar_dados_cep(cep):
    """Busca dados de endereço pelo CEP usando a API ViaCEP."""
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def gerenciamento_empresas():
    st.title("Gerenciamento de Empresas")
    collection_empresas = get_collection("empresas")
    collection_usuarios = get_collection("usuarios")

    # Variáveis para preenchimento automático
    dados_cnpj = {}
    dados_cep = {}

    # Buscar CNPJ antes de exibir o formulário
    st.subheader("Busca Automática de CNPJ e CEP")
    with st.expander("Preencher Dados com CNPJ e CEP"):
        cnpj_input = st.text_input("CNPJ", max_chars=18)
        if st.button("Buscar Dados do CNPJ"):
            dados_cnpj = buscar_dados_cnpj(cnpj_input)
            if dados_cnpj and not dados_cnpj.get("erro"):
                st.success("Dados do CNPJ encontrados!")
            else:
                st.error("CNPJ não encontrado ou inválido!")
                dados_cnpj = {}

        cep_input = st.text_input("CEP", max_chars=10)
        if st.button("Buscar Dados do CEP"):
            dados_cep = buscar_dados_cep(cep_input)
            if dados_cep and not dados_cep.get("erro"):
                st.success("Dados do CEP encontrados!")
            else:
                st.error("CEP não encontrado ou inválido!")
                dados_cep = {}

    # Obter usuários cadastrados
    usuarios = list(collection_usuarios.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))
    opcoes_usuarios = [f"{u['nome']} {u['sobrenome']} ({u['email']})" for u in usuarios]

    if not usuarios:
        st.warning("Nenhum usuário encontrado. Cadastre um usuário primeiro antes de adicionar empresas.")
    else:
        # Formulário principal
        st.subheader("Cadastrar Empresa")
        with st.form(key="form_cadastro_empresa"):
            razao_social = st.text_input("Razão Social", value=dados_cnpj.get("nome", ""))
            cnpj = st.text_input("CNPJ", value=cnpj_input, max_chars=18)
            rua = st.text_input("Rua", value=dados_cnpj.get("logradouro", dados_cep.get("logradouro", "")))
            bairro = st.text_input("Bairro", value=dados_cnpj.get("bairro", dados_cep.get("bairro", "")))
            cidade = st.text_input("Cidade", value=dados_cnpj.get("municipio", dados_cep.get("localidade", "")))
            estado = st.text_input("Estado", value=dados_cnpj.get("uf", dados_cep.get("uf", "")))
            cep = st.text_input("CEP", value=dados_cnpj.get("cep", cep_input), max_chars=10)
            site = st.text_input("Site")
            fone = st.text_input("Telefone", value=dados_cnpj.get("telefone", ""))
            insc_estadual = st.text_input("Inscrição Estadual")
            setor = st.text_input("Setor")
            tamanho_empresa = st.selectbox("Tamanho da Empresa", ["Pequena", "Média", "Grande"])
            usuario = st.selectbox("Usuário Associado", options=opcoes_usuarios)
            documentos = st.file_uploader("Documentos", accept_multiple_files=True)

            submit = st.form_submit_button("Cadastrar")

            if submit:
                if razao_social and cnpj:
                    # Verificar duplicidade no banco de empresas
                    existing_company = collection_empresas.find_one({"cnpj": cnpj})
                    if existing_company:
                        st.error("Empresa já cadastrada com este CNPJ!")
                    else:
                        documentos_salvos = [{"nome_documento": doc.name, "tipo": doc.type} for doc in documentos] if documentos else []

                        # Criar o documento da empresa
                        document = {
                            "razao_social": razao_social,
                            "cnpj": cnpj,
                            "rua": rua,
                            "cep": cep,
                            "bairro": bairro,
                            "cidade": cidade,
                            "estado": estado,
                            "site": site,
                            "fone": fone,
                            "insc_estadual": insc_estadual,
                            "setor": setor,
                            "tamanho_empresa": tamanho_empresa,
                            "usuario": usuario.split("(")[-1].strip(")"),
                            "documentos": documentos_salvos,
                        }
                        collection_empresas.insert_one(document)
                        st.success("Empresa cadastrada com sucesso!")
                else:
                    st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ).")