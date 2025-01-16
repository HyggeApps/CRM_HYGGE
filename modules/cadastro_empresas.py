import streamlit as st
import requests
from utils.database import get_collection

def buscar_dados_cnpj(cnpj):
    """Busca dados de uma empresa pelo CNPJ usando a API ReceitaWS."""
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
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
    collection_usuarios = get_collection("usuarios")  # Coleção para listar usuários

    # Abas para gerenciar empresas
    tab1, tab2, tab3, tab4 = st.tabs(["Cadastrar Empresa", "Cadastrar SubEmpresa", "Remover Empresa", "Exibir Empresas"])

    # Aba: Cadastrar Empresa
    with tab1:
        st.header("Cadastrar Empresa")

        # Obter usuários cadastrados
        usuarios = list(collection_usuarios.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))
        opcoes_usuarios = [f"{u['nome']} {u['sobrenome']} ({u['email']})" for u in usuarios]

        if not usuarios:
            st.warning("Nenhum usuário encontrado. Cadastre um usuário primeiro antes de adicionar empresas.")
        else:
            with st.form(key="form_cadastro_empresa"):
                cnpj = st.text_input("CNPJ", key="input_cnpj")

                # Buscar dados do CNPJ
                if st.button("Buscar Dados do CNPJ"):
                    dados_cnpj = buscar_dados_cnpj(cnpj)
                    if dados_cnpj and not dados_cnpj.get("erro"):
                        razao_social = dados_cnpj.get("nome", "")
                        rua = dados_cnpj.get("logradouro", "")
                        bairro = dados_cnpj.get("bairro", "")
                        cidade = dados_cnpj.get("municipio", "")
                        estado = dados_cnpj.get("uf", "")
                        cep = dados_cnpj.get("cep", "").replace(".", "").replace("-", "")
                        st.success("Dados preenchidos automaticamente!")
                    else:
                        st.error("CNPJ não encontrado ou inválido!")
                        razao_social, rua, bairro, cidade, estado, cep = "", "", "", "", "", ""
                else:
                    razao_social, rua, bairro, cidade, estado, cep = "", "", "", "", "", ""

                razao_social = st.text_input("Razão Social", value=razao_social, key="input_razao_social")
                rua = st.text_input("Rua", value=rua, key="input_rua")
                bairro = st.text_input("Bairro", value=bairro, key="input_bairro")
                cidade = st.text_input("Cidade", value=cidade, key="input_cidade")
                estado = st.text_input("Estado", value=estado, key="input_estado")
                cep = st.text_input("CEP", value=cep, key="input_cep")

                # Buscar dados do CEP
                if st.button("Buscar Dados do CEP"):
                    dados_cep = buscar_dados_cep(cep)
                    if dados_cep and not dados_cep.get("erro"):
                        rua = dados_cep.get("logradouro", "")
                        bairro = dados_cep.get("bairro", "")
                        cidade = dados_cep.get("localidade", "")
                        estado = dados_cep.get("uf", "")
                        st.success("Endereço preenchido automaticamente!")
                    else:
                        st.error("CEP não encontrado ou inválido!")
                        rua, bairro, cidade, estado = "", "", "", ""

                site = st.text_input("Site", key="input_site")
                fone = st.text_input("Telefone", key="input_fone")
                insc_estadual = st.text_input("Inscrição Estadual", key="input_insc_estadual")
                setor = st.text_input("Setor", key="input_setor")
                tamanho_empresa = st.selectbox("Tamanho da Empresa", ["Pequena", "Média", "Grande"], key="input_tamanho_empresa")
                usuario = st.selectbox("Usuário Associado", options=opcoes_usuarios, key="select_usuario")
                documentos = st.file_uploader("Documentos", accept_multiple_files=True, key="input_documentos")

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