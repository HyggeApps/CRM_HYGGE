import streamlit as st
import requests
from utils.database import get_collection
import pandas as pd

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
    with st.expander("Preencher Dados com CNPJ e CEP (dois cliques para buscar)"):
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


def consultar_empresas():
    collection_empresas = get_collection("empresas")

    # Obter lista de vendedores
    vendedores = list(collection_empresas.distinct("usuario"))
    vendedores = [v for v in vendedores if v]

    # Filtros
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        filtro_razao_social = st.text_input("Nome", placeholder="Parte do nome da empresa")
    with col2:
        filtro_cidade = st.text_input("Cidade", placeholder="Digite a cidade")
    with col3:
        filtro_estado = st.text_input("Estado (UF)", max_chars=2, placeholder="Ex: SP")
    with col4:
        filtro_tamanho = st.multiselect(
            "Tamanho",
            options=["Tier 1", "Tier 2", "Tier 3", "Tier 4"],
            default=[],
        )
    with col5:
        filtro_vendedor = st.selectbox(
            "Proprietário",
            options=["Todos"] + vendedores,
            index=0,
        )
    with col6:
        filtro_data_criacao = st.date_input("Data da última atividade", value=None)

    # Construir query de filtro
    query = {}
    if filtro_razao_social:
        query["razao_social"] = {"$regex": filtro_razao_social, "$options": "i"}
    if filtro_cidade:
        query["cidade"] = {"$regex": filtro_cidade, "$options": "i"}
    if filtro_estado:
        query["estado"] = filtro_estado.upper()
    if filtro_tamanho:
        query["tamanho_empresa"] = {"$in": filtro_tamanho}
    if filtro_vendedor and filtro_vendedor != "Todos":
        query["usuario"] = filtro_vendedor
    if filtro_data_criacao:
        query["data_criacao"] = {"$gte": filtro_data_criacao.strftime("%Y-%m-%d")}

    # Buscar empresas no banco de dados com os filtros aplicados
    empresas_filtradas = list(
        collection_empresas.find(
            query,
            {
                "_id": 0,
                "razao_social": 1,
                "usuario": 1,
                "data_criacao": 1,  # Assumindo que esta seja a data da última atividade
                "cidade": 1,
                "estado": 1,
                "tamanho_empresa": 1,
            },
        )
    )

    # Exibir tabela ou mensagem de alerta
    if empresas_filtradas:
        df_empresas = pd.DataFrame(empresas_filtradas)

        # Renomear colunas conforme solicitado
        df_empresas = df_empresas.rename(
            columns={
                "razao_social": "Nome",
                "usuario": "Proprietário",
                "data_criacao": "Última Atividade",
                "cidade": "Cidade",
                "estado": "UF",
                "tamanho_empresa": "Tamanho",
            }
        )

        # Converter a data de string para formato legível
        df_empresas["Última Atividade"] = pd.to_datetime(df_empresas["Última Atividade"], errors="coerce").dt.strftime("%d/%m/%Y")

        # Adicionar coluna de seleção como primeiro campo
        df_empresas.insert(0, "Selecionada", False)

        # Inicializar seleção no session_state
        if "empresa_selecionada" not in st.session_state:
            st.session_state["empresa_selecionada"] = None

        # Criar tabela interativa com `st.data_editor()`
        edited_df = st.data_editor(
            df_empresas,
            column_config={
                "Selecionada": st.column_config.CheckboxColumn(
                    "Selecionar",
                    help="Marque para ver detalhes da empresa",
                ),
            },
            disabled=["Nome", "Proprietário", "Última Atividade", "Cidade", "UF", "Tamanho"],
            hide_index=True,
            use_container_width=True  # Faz a tabela ocupar toda a largura da tela
        )

        # Garantir que apenas uma empresa esteja selecionada
        if edited_df["Selecionada"].sum() > 1:
            last_selected_index = edited_df[edited_df["Selecionada"]].index[-1]
            edited_df["Selecionada"] = False
            edited_df.at[last_selected_index, "Selecionada"] = True

        # Atualizar `st.session_state` com a empresa selecionada
        if edited_df["Selecionada"].any():
            selected_index = edited_df[edited_df["Selecionada"]].index[0]
            st.session_state["empresa_selecionada"] = edited_df.iloc[selected_index].to_dict()
        else:
            st.session_state["empresa_selecionada"] = None

        # Exibir os detalhes da empresa selecionada abaixo da tabela
        if st.session_state["empresa_selecionada"]:
            empresa = st.session_state["empresa_selecionada"]
            st.write("### 🔍 Detalhes da Empresa Selecionada")
            st.write(f"**Nome:** {empresa['Nome']}")
            st.write(f"**Proprietário:** {empresa['Proprietário']}")
            st.write(f"**Última Atividade:** {empresa['Última Atividade']}")
            st.write(f"**Cidade:** {empresa['Cidade']}, {empresa['UF']}")
            st.write(f"**Tamanho:** {empresa['Tamanho']}")
        else:
            st.info("Selecione uma empresa para ver os detalhes.")

    else:
        st.warning("Nenhuma empresa encontrada com os critérios aplicados.")


def cadastrar_subempresa():
    
    collection_empresas = get_collection("empresas")
    collection_subempresas = get_collection("subempresas")

    st.header("Cadastrar sub-empresa na base de dados da HYGGE")
    st.info("Cadastre aqui uma sub-empresa ou variação da empresa matriz.")
    st.write('---')

    # Obter empresas matriz cadastradas
    empresas_matriz = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
    opcoes_matriz = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas_matriz]

    if not empresas_matriz:
        st.warning("Nenhuma empresa matriz encontrada. Cadastre uma empresa matriz antes de adicionar subempresas.")
    else:
        # Variáveis para preenchimento automático e controle de botões
        if "dados_cnpj_sub" not in st.session_state:
            st.session_state["dados_cnpj_sub"] = {}
        if "dados_cep_sub" not in st.session_state:
            st.session_state["dados_cep_sub"] = {}
        if "buscar_cnpj_sub_clicked" not in st.session_state:
            st.session_state["buscar_cnpj_sub_clicked"] = False
        if "buscar_cep_sub_clicked" not in st.session_state:
            st.session_state["buscar_cep_sub_clicked"] = False

        st.subheader("Busca Automática de CNPJ e CEP")
        with st.expander("Preencher Dados com CNPJ e CEP (dois cliques para buscar)"):
            col1, col2 = st.columns(2)
            with col1:
                cnpj_input = st.text_input("CNPJ da sub-empresa", max_chars=18, placeholder="Digite o CNPJ (com ou sem formatação)", key="cnpj_input_sub")
                buscar_cnpj = st.button("Buscar Dados do CNPJ (sub-empresa)", key="buscar_cnpj_sub")
            with col2:
                cep_input = st.text_input("CEP da sub-empresa", max_chars=10, placeholder="Digite o CEP (com ou sem formatação)", key="cep_input_sub")
                buscar_cep = st.button("Buscar Dados do CEP (sub-empresa)", key="buscar_cep_sub")

            if buscar_cnpj and not st.session_state["buscar_cnpj_sub_clicked"]:
                st.session_state["buscar_cnpj_sub_clicked"] = True
                cnpj_limpo = cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
                if len(cnpj_limpo) == 14:
                    dados_cnpj = buscar_dados_cnpj(cnpj_limpo)
                    if dados_cnpj and not dados_cnpj.get("erro"):
                        st.success("Dados do CNPJ encontrados!")
                        st.session_state["dados_cnpj_sub"] = dados_cnpj
                    else:
                        st.error("CNPJ não encontrado ou inválido!")
                        st.session_state["dados_cnpj_sub"] = {}
                else:
                    st.error("CNPJ inválido! Certifique-se de que o CNPJ tem 14 dígitos.")
                st.session_state["buscar_cnpj_sub_clicked"] = False

            if buscar_cep and not st.session_state["buscar_cep_sub_clicked"]:
                st.session_state["buscar_cep_sub_clicked"] = True
                cep_limpo = cep_input.replace("-", "").replace(" ", "")
                if len(cep_limpo) == 8:
                    dados_cep = buscar_dados_cep(cep_limpo)
                    if dados_cep and not dados_cep.get("erro"):
                        st.success("Dados do CEP encontrados!")
                        st.session_state["dados_cep_sub"] = dados_cep
                    else:
                        st.error("CEP não encontrado ou inválido!")
                        st.session_state["dados_cep_sub"] = {}
                else:
                    st.error("CEP inválido! Certifique-se de que o CEP tem 8 dígitos.")
                st.session_state["buscar_cep_sub_clicked"] = False

        # Formulário de Cadastro de sub-empresa
        with st.form(key="form_cadastro_subempresa"):
            st.subheader("Formulário de Cadastro de sub-empresa")

            # Linha 1: Empresa Matriz e Razão Social
            col1, col2 = st.columns(2)
            with col1:
                empresa_matriz = st.selectbox("Empresa Matriz *", options=opcoes_matriz, key="select_empresa_matriz")
            with col2:
                razao_social = st.text_input("Razão Social da sub-empresa *", value=st.session_state["dados_cnpj_sub"].get("nome", ""), key="input_razao_social_subempresa")

            # Linha 2: CNPJ e Telefone
            col3, col4 = st.columns(2)
            with col3:
                cnpj = st.text_input("CNPJ da sub-empresa *", value=cnpj_input, max_chars=18, key="input_cnpj_subempresa")
            with col4:
                fone = st.text_input("Telefone", value=st.session_state["dados_cnpj_sub"].get("telefone", ""), key="input_fone_subempresa")

            # Linha 3: Rua e Bairro
            col5, col6 = st.columns(2)
            with col5:
                rua = st.text_input("Rua", value=st.session_state["dados_cnpj_sub"].get("logradouro", st.session_state["dados_cep_sub"].get("logradouro", "")), key="input_rua_subempresa")
            with col6:
                bairro = st.text_input("Bairro", value=st.session_state["dados_cnpj_sub"].get("bairro", st.session_state["dados_cep_sub"].get("bairro", "")), key="input_bairro_subempresa")

            # Linha 4: Cidade, Estado e CEP
            col7, col8, col9 = st.columns(3)
            with col7:
                cidade = st.text_input("Cidade", value=st.session_state["dados_cnpj_sub"].get("municipio", st.session_state["dados_cep_sub"].get("localidade", "")), key="input_cidade_subempresa")
            with col8:
                estado = st.text_input("Estado", value=st.session_state["dados_cnpj_sub"].get("uf", st.session_state["dados_cep_sub"].get("uf", "")), key="input_estado_subempresa")
            with col9:
                cep = st.text_input("CEP", value=cep_input, max_chars=10, key="input_cep_subempresa")

            # Botão para cadastrar
            submit_sub = st.form_submit_button("Cadastrar sub-empresa")

            if submit_sub:
                if razao_social and cnpj and empresa_matriz:
                    matriz_cnpj = empresa_matriz.split("CNPJ: ")[-1].strip(")")
                    existing_subempresa = collection_subempresas.find_one({"cnpj": cnpj})
                    if existing_subempresa:
                        st.error("Sub-empresa já cadastrada com este CNPJ!")
                    else:
                        document = {
                            "empresa_matriz": matriz_cnpj,
                            "razao_social": razao_social,
                            "cnpj": cnpj,
                            "rua": rua,
                            "cep": cep,
                            "bairro": bairro,
                            "cidade": cidade,
                            "estado": estado,
                            "fone": fone,
                        }
                        collection_subempresas.insert_one(document)
                        # Atualizar lista de subempresas na matriz
                        collection_empresas.update_one(
                            {"cnpj": matriz_cnpj},
                            {"$push": {"subempresas": cnpj}}
                        )
                        st.success("Sub-empresa cadastrada e vinculada à matriz com sucesso!")
                else:
                    st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ, Empresa Matriz).")