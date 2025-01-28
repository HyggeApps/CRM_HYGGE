import streamlit as st
import requests
from utils.database import get_collection

def buscar_dados_cnpj(cnpj):
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def buscar_dados_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def cadastrar_empresas(user, admin):
    collection_empresas = get_collection("empresas")
    # -------------------
    # Aba: Cadastrar Empresa
    # -------------------
    st.header("Cadastrar nova empresa na base de dados da HYGGE")
    st.info("Busque automaticamente informações da empresa a partir do CNPJ e/ou CEP e preencha os demais campos no formulário abaixo.")
    st.write('---')

    # Variáveis para preenchimento automático
    if "dados_cnpj" not in st.session_state:
        st.session_state["dados_cnpj"] = {}
    if "dados_cep" not in st.session_state:
        st.session_state["dados_cep"] = {}
    if "buscar_cnpj_clicked" not in st.session_state:
        st.session_state["buscar_cnpj_clicked"] = False
    if "buscar_cep_clicked" not in st.session_state:
        st.session_state["buscar_cep_clicked"] = False

    # Buscar CNPJ antes de exibir o formulário
    st.subheader("Busca Automática de CNPJ e CEP")
    with st.expander("Preencher Dados com CNPJ e CEP"):
        col1, col2 = st.columns(2)
        with col1:
            cnpj_input = st.text_input("CNPJ", max_chars=18, placeholder="Digite o CNPJ (com ou sem formatação)", key="cnpj_input")
            if st.button("Buscar Dados do CNPJ", key="buscar_cnpj"):
                cnpj_limpo = cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
                if len(cnpj_limpo) == 14:
                    dados_cnpj = buscar_dados_cnpj(cnpj_limpo)
                    if dados_cnpj and not dados_cnpj.get("erro"):
                        st.success("Dados do CNPJ encontrados!")
                        st.session_state["dados_cnpj"] = dados_cnpj
                    else:
                        st.error("CNPJ não encontrado ou inválido!")
                        st.session_state["dados_cnpj"] = {}
                else:
                    st.error("CNPJ inválido! Certifique-se de que o CNPJ tem 14 dígitos.")

        with col2:
            cep_input = st.text_input("CEP", max_chars=10, placeholder="Digite o CEP (com ou sem formatação)", key="cep_input")
            if st.button("Buscar Dados do CEP", key="buscar_cep"):
                cep_limpo = cep_input.replace("-", "").replace(" ", "")
                if len(cep_limpo) == 8:
                    dados_cep = buscar_dados_cep(cep_limpo)
                    if dados_cep and not dados_cep.get("erro"):
                        st.success("Dados do CEP encontrados!")
                        st.session_state["dados_cep"] = dados_cep
                    else:
                        st.error("CEP não encontrado ou inválido!")
                        st.session_state["dados_cep"] = {}
                else:
                    st.error("CEP inválido! Certifique-se de que o CEP tem 8 dígitos.")


    # Formulário principal
    st.subheader("Formulário de cadastro")
    with st.form(key="form_cadastro_empresa"):

        # Primeira linha: Razão Social e CNPJ
        col1, col2 = st.columns(2)
        with col1:
            razao_social = st.text_input("Nome da Empresa *", value=st.session_state["dados_cnpj"].get("nome", ""), key="razao_social")
        with col2:
            cnpj = st.text_input("CNPJ *", value=cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", ""), max_chars=18, key="cnpj")

        # Segunda linha: Rua e Bairro
        col3, col4 = st.columns(2)
        with col3:
            rua = st.text_input("Rua", value=st.session_state["dados_cnpj"].get("logradouro", st.session_state["dados_cep"].get("logradouro", "")), key="rua")
        with col4:
            bairro = st.text_input("Bairro", value=st.session_state["dados_cnpj"].get("bairro", st.session_state["dados_cep"].get("bairro", "")), key="bairro")

        # Terceira linha: Cidade, Estado e CEP
        col5, col6, col7 = st.columns(3)
        with col5:
            cidade = st.text_input("Cidade *", value=st.session_state["dados_cnpj"].get("municipio", st.session_state["dados_cep"].get("localidade", "")), key="cidade")
        with col6:
            estado = st.text_input("Estado", value=st.session_state["dados_cnpj"].get("uf", st.session_state["dados_cep"].get("uf", "")), key="estado")
        with col7:
            cep = st.text_input("CEP", value=cep_input, max_chars=10, key="cep")

        # Quarta linha: Telefone e Site
        col8, col9 = st.columns(2)
        with col8:
            fone = st.text_input("Telefone", value=st.session_state["dados_cnpj"].get("telefone", ""), key="fone")
        with col9:
            site = st.text_input("Site", key="site")

        # Quinta linha: Inscrição Estadual e Setor
        col10, col11 = st.columns(2)
        with col10:
            insc_estadual = st.text_input("Inscrição Estadual", key="insc_estadual")
        with col11:
            setor = st.selectbox("Setor *", ["Comercial", "Residencial", "Residencial MCMV", "Industrial"], key="setor")

        # Sexta linha: Tamanho da Empresa
        col12, col13 = st.columns(2)
        with col12:
            produto_interesse = st.selectbox("Produto de Interesse *", ["NBR Fast", "Consultoria NBR", "Consultoria HYGGE", "Consultoria Certificação"], key="produto_interesse")
        with col13:
            tamanho_empresa = st.selectbox("Tamanho da Empresa *", ["Tier 1", "Tier 2", "Tier 3", "Tier 4"], key="tamanho_empresa")
        
            
        clear = st.form_submit_button("Limpar")
        submit = st.form_submit_button("Cadastrar")

        if submit:
            # Verifica se os campos obrigatórios foram preenchidos
            if not razao_social:
                st.error("O campo 'Nome da Empresa' é obrigatório.")
            elif not cnpj:
                st.error("O campo 'CNPJ' é obrigatório.")
            elif not cidade:
                st.error("O campo 'Cidade' é obrigatório.")
            elif not setor:
                st.error("O campo 'Setor' é obrigatório.")
            elif not produto_interesse:
                st.error("O campo 'Produto de Interesse' é obrigatório.")
            elif not tamanho_empresa:
                st.error("O campo 'Tamanho da Empresa' é obrigatório.")
            else:
                # Verifica se a empresa já está cadastrada
                existing_company = collection_empresas.find_one({"cnpj": cnpj})
                if existing_company:
                    st.error("Empresa já cadastrada com este CNPJ!")
                else:
                    # Insere os dados na coleção
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
                        "produto_interesse": produto_interesse,
                        "usuario": user,
                    }
                    collection_empresas.insert_one(document)
                    st.success("Empresa cadastrada com sucesso!")

        if clear:
            # Limpar os valores de `st.session_state` antes de recarregar os widgets
            for key in [
                "dados_cnpj", "dados_cep", "cnpj_input", "cep_input", "razao_social", "cnpj",
                "rua", "bairro", "cidade", "estado", "cep", "fone", "site",
                "insc_estadual", "setor", "produto_interesse", "tamanho_empresa"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


