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
        
        # Botão de cadastro
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


def consultar_empresas():
    collection_empresas = get_collection("empresas")
    st.header("Empresas cadastradas na base de dados da HYGGE")
    st.info("Visualize e filtre as empresas cadastradas na nossa base de dados.")
    st.write('----')

    # Obter lista de vendedores
    vendedores = list(collection_empresas.distinct("usuario"))
    vendedores = [v for v in vendedores if v]

    # Filtros
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        filtro_razao_social = st.text_input("Razão Social", placeholder="Parte da Razão Social")
    with col2:
        filtro_cnpj = st.text_input("CNPJ", placeholder="Parte do CNPJ")
    with col3:
        filtro_cidade = st.text_input("Cidade", placeholder="Digite a cidade")
    with col4:
        filtro_estado = st.text_input("Estado (UF)", max_chars=2, placeholder="Ex: SP")
    with col5:
        filtro_tamanho = st.multiselect(
            "Tamanho",
            options=["Pequena", "Média", "Grande"],
            default=[],
        )
    with col6:
        filtro_vendedor = st.selectbox(
            "Vendedor",
            options=["Todos"] + vendedores,
            index=0,
        )

    # Construir query de filtro
    query = {}
    if filtro_razao_social:
        query["razao_social"] = {"$regex": filtro_razao_social, "$options": "i"}
    if filtro_cnpj:
        query["cnpj"] = {"$regex": filtro_cnpj, "$options": "i"}
    if filtro_cidade:
        query["cidade"] = {"$regex": filtro_cidade, "$options": "i"}
    if filtro_estado:
        query["estado"] = filtro_estado.upper()
    if filtro_tamanho:
        query["tamanho_empresa"] = {"$in": filtro_tamanho}
    if filtro_vendedor and filtro_vendedor != "Todos":
        query["usuario"] = filtro_vendedor

    # Buscar empresas no banco de dados com os filtros aplicados
    empresas_filtradas = list(
        collection_empresas.find(
            query,
            {
                "_id": 0,
                "razao_social": 1,
                "cnpj": 1,
                "cidade": 1,
                "estado": 1,
                "pais": 1,
                "tamanho_empresa": 1,
                "usuario": 1,
            },
        )
    )

    # Exibir tabela ou mensagem de alerta
    if empresas_filtradas:
        import pandas as pd

        df_empresas = pd.DataFrame(empresas_filtradas)
        df_empresas = df_empresas.rename(
            columns={
                "razao_social": "Razão Social",
                "cnpj": "CNPJ",
                "cidade": "Cidade",
                "estado": "UF",
                "pais": "País",
                "tamanho_empresa": "Tamanho",
                "usuario": "Vendedor",
            }
        )
        st.dataframe(df_empresas, use_container_width=True)
    else:
        st.warning("Nenhuma empresa encontrada com os critérios aplicados.")

def gerenciamento_empresas(user, admin):
    collection_empresas = get_collection("empresas")
    collection_usuarios = get_collection("usuarios")
    collection_subempresas = get_collection("subempresas")

    tab1_1, tab1_2, tab1_3, tab1_4, tab1_5, tab1_6 = st.tabs([
        "Empresas cadastradas", "Editar empresa", "Cadastrar empresa", "Remover empresa", "Cadastrar sub-empresa", "Remover sub-empresa"
    ])

    # -------------------
    # Aba: Exibir Empresas com Filtros
    # -------------------
    with tab1_1:
        st.header("Empresas cadastradas na base de dados da HYGGE")
        st.info("Visualize e filtre as empresas cadastradas na nossa base de dados.")
        st.write('----')

        # Obter lista de vendedores
        vendedores = list(collection_empresas.distinct("usuario"))
        vendedores = [v for v in vendedores if v]

        # Filtros
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            filtro_razao_social = st.text_input("Razão Social", placeholder="Parte da Razão Social")
        with col2:
            filtro_cnpj = st.text_input("CNPJ", placeholder="Parte do CNPJ")
        with col3:
            filtro_cidade = st.text_input("Cidade", placeholder="Digite a cidade")
        with col4:
            filtro_estado = st.text_input("Estado (UF)", max_chars=2, placeholder="Ex: SP")
        with col5:
            filtro_tamanho = st.multiselect(
                "Tamanho",
                options=["Pequena", "Média", "Grande"],
                default=[],
            )
        with col6:
            filtro_vendedor = st.selectbox(
                "Vendedor",
                options=["Todos"] + vendedores,
                index=0,
            )

        # Construir query de filtro
        query = {}
        if filtro_razao_social:
            query["razao_social"] = {"$regex": filtro_razao_social, "$options": "i"}
        if filtro_cnpj:
            query["cnpj"] = {"$regex": filtro_cnpj, "$options": "i"}
        if filtro_cidade:
            query["cidade"] = {"$regex": filtro_cidade, "$options": "i"}
        if filtro_estado:
            query["estado"] = filtro_estado.upper()
        if filtro_tamanho:
            query["tamanho_empresa"] = {"$in": filtro_tamanho}
        if filtro_vendedor and filtro_vendedor != "Todos":
            query["usuario"] = filtro_vendedor

        # Buscar empresas no banco de dados com os filtros aplicados
        empresas_filtradas = list(
            collection_empresas.find(
                query,
                {
                    "_id": 0,
                    "razao_social": 1,
                    "cnpj": 1,
                    "cidade": 1,
                    "estado": 1,
                    "pais": 1,
                    "tamanho_empresa": 1,
                    "usuario": 1,
                },
            )
        )

        # Exibir tabela ou mensagem de alerta
        if empresas_filtradas:
            import pandas as pd

            df_empresas = pd.DataFrame(empresas_filtradas)
            df_empresas = df_empresas.rename(
                columns={
                    "razao_social": "Razão Social",
                    "cnpj": "CNPJ",
                    "cidade": "Cidade",
                    "estado": "UF",
                    "pais": "País",
                    "tamanho_empresa": "Tamanho",
                    "usuario": "Vendedor",
                }
            )
            st.dataframe(df_empresas, use_container_width=True)
        else:
            st.warning("Nenhuma empresa encontrada com os critérios aplicados.")

    # -------------------
    # Aba: Editar Empresa
    # -------------------
    with tab1_2:
        st.header("Editar Empresa")
        st.info("Selecione uma empresa para editar as informações cadastradas.")
        st.write("---")

        empresas = list(collection_empresas.find({"usuario": user}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        opcoes_empresas = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas]

        if not empresas:
            st.warning("Nenhuma empresa cadastrada por você foi encontrada. Cadastre uma empresa antes de tentar editar.")
        else:
            empresa_selecionada = st.selectbox("Selecione a Empresa para Editar", options=opcoes_empresas, key="empresa_editar")

            if empresa_selecionada:
                cnpj_editar = empresa_selecionada.split("CNPJ: ")[-1].strip(")")
                empresa_dados = collection_empresas.find_one({"cnpj": cnpj_editar}, {"_id": 0})

                if empresa_dados:
                    with st.form(key="form_editar_empresa"):
                        col1, col2 = st.columns(2)
                        with col1:
                            razao_social = st.text_input("Razão Social", value=empresa_dados.get("razao_social", ""), key="edit_razao_social")
                        with col2:
                            cnpj = st.text_input("CNPJ", value=empresa_dados.get("cnpj", ""), disabled=True, key="edit_cnpj")

                        col3, col4 = st.columns(2)
                        with col3:
                            rua = st.text_input("Rua", value=empresa_dados.get("rua", ""), key="edit_rua")
                        with col4:
                            bairro = st.text_input("Bairro", value=empresa_dados.get("bairro", ""), key="edit_bairro")

                        col5, col6, col7 = st.columns(3)
                        with col5:
                            cidade = st.text_input("Cidade", value=empresa_dados.get("cidade", ""), key="edit_cidade")
                        with col6:
                            estado = st.text_input("Estado", value=empresa_dados.get("estado", ""), max_chars=2, key="edit_estado")
                        with col7:
                            cep = st.text_input("CEP", value=empresa_dados.get("cep", ""), max_chars=10, key="edit_cep")

                        col8, col9 = st.columns(2)
                        with col8:
                            fone = st.text_input("Telefone", value=empresa_dados.get("fone", ""), key="edit_fone")
                        with col9:
                            site = st.text_input("Site", value=empresa_dados.get("site", ""), key="edit_site")

                        col10, col11 = st.columns(2)
                        with col10:
                            insc_estadual = st.text_input("Inscrição Estadual", value=empresa_dados.get("insc_estadual", ""), key="edit_insc_estadual")
                        with col11:
                            setor = st.selectbox(
                                "Setor",
                                ["Comercial", "Residencial", "Residencial MCMV", "Industrial"],
                                index=["Comercial", "Residencial", "Residencial MCMV", "Industrial"].index(empresa_dados.get("setor", "Comercial")),
                                key="edit_setor"
                            )

                        col12 = st.columns(1)
                        with col12[0]:
                            tamanho_empresa = st.selectbox(
                                "Tamanho da Empresa",
                                ["Pequena", "Média", "Grande"],
                                index=["Pequena", "Média", "Grande"].index(empresa_dados.get("tamanho_empresa", "Pequena")),
                                key="edit_tamanho_empresa"
                            )

                        submit_editar = st.form_submit_button("Salvar Alterações")

                        if submit_editar:
                            document_update = {
                                "razao_social": razao_social,
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
                            }
                            collection_empresas.update_one({"cnpj": cnpj_editar}, {"$set": document_update})
                            st.success("Empresa atualizada com sucesso!")




        # -------------------
        # Aba: Remover Empresa
        # -------------------
        with tab1_4:
            st.header("Remover empresa na base de dados da HYGGE")
            st.info("Selecione na lista suspensa abaixo a empresa para removê-la. **Observação: Apenas empresas cadastradas pelo seu usuário podem ser deletadas.**")
            st.write('---')

            # Inicializar o estado de remoção
            if "remover_empresa_clicked" not in st.session_state:
                st.session_state["remover_empresa_clicked"] = False

            # Filtrar empresas vinculadas ao vendedor
            empresas = list(collection_empresas.find({"usuario": user}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
            opcoes_empresas = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas]

            if not empresas:
                st.warning("Nenhuma empresa vinculada ao vendedor encontrada para remoção.")
            else:
                # Formulário para remoção
                with st.form(key="form_remover_empresa"):
                    empresa_selecionada = st.selectbox("Selecione a empresa que deseja remover", options=opcoes_empresas)
                    remove_submit = st.form_submit_button("Remover Empresa")

                    if remove_submit and not st.session_state["remover_empresa_clicked"]:
                        st.session_state["remover_empresa_clicked"] = True
                        cnpj_remover = empresa_selecionada.split("CNPJ: ")[-1].strip(")")

                        # Realizar a remoção
                        result = collection_empresas.delete_one({"cnpj": cnpj_remover, "usuario": user})  # Garante que só remove se o vendedor for o usuário

                        if result.deleted_count > 0:
                            st.success(f"Empresa com CNPJ '{cnpj_remover}' removida com sucesso!")
                        else:
                            st.error(f"Erro ao remover a empresa com CNPJ '{cnpj_remover}'. Verifique se você tem permissão para removê-la.")
                        
                        # Resetar o estado após o processamento
                        st.session_state["remover_empresa_clicked"] = False

        # -------------------
        # Aba: Cadastrar SubEmpresa
        # -------------------
        with tab1_5:
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
                with st.expander("Preencher Dados com CNPJ e CEP"):
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
                        empresa_matriz = st.selectbox("Empresa Matriz", options=opcoes_matriz, key="select_empresa_matriz")
                    with col2:
                        razao_social = st.text_input("Razão Social da sub-empresa", value=st.session_state["dados_cnpj_sub"].get("nome", ""), key="input_razao_social_subempresa")

                    # Linha 2: CNPJ e Telefone
                    col3, col4 = st.columns(2)
                    with col3:
                        cnpj = st.text_input("CNPJ da sub-empresa", value=cnpj_input, max_chars=18, key="input_cnpj_subempresa")
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

        # -------------------
        # Aba: Remover sub-empresa
        # -------------------
        with tab1_6:
            st.subheader("Remover sub-empresa")
            
            # Obter subempresas cadastradas
            subempresas = list(collection_subempresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1, "empresa_matriz": 1}))
            opcoes_subempresas = [f"{s['razao_social']} (CNPJ: {s['cnpj']}) - Matriz: {s['empresa_matriz']}" for s in subempresas]

            if not subempresas:
                st.warning("Nenhuma subempresa encontrada para remoção.")
            else:
                # Controle de estado do botão
                if "remover_subempresa_clicked" not in st.session_state:
                    st.session_state["remover_subempresa_clicked"] = False

                with st.form(key="form_remover_subempresa"):
                    # Selecionar subempresa para remoção
                    subempresa_selecionada = st.selectbox("Selecione a sub-empresa para removê-la", options=opcoes_subempresas, key="select_remover_subempresa")
                    remove_submit = st.form_submit_button("Remover sub-empresa")

                    if remove_submit and not st.session_state["remover_subempresa_clicked"]:
                        st.session_state["remover_subempresa_clicked"] = True
                        cnpj_remover = subempresa_selecionada.split("CNPJ: ")[-1].split(")")[0]
                        empresa_matriz = subempresa_selecionada.split("Matriz: ")[-1]

                        # Remover subempresa do banco de subempresas
                        result = collection_subempresas.delete_one({"cnpj": cnpj_remover})
                        if result.deleted_count > 0:
                            # Atualizar a lista de subempresas na matriz
                            collection_empresas.update_one(
                                {"cnpj": empresa_matriz},
                                {"$pull": {"subempresas": cnpj_remover}}
                            )
                            st.success(f"Sub-empresa com CNPJ '{cnpj_remover}' removida com sucesso e desvinculada da matriz '{empresa_matriz}'!")
                        else:
                            st.error(f"Erro ao remover a subempresa com CNPJ '{cnpj_remover}'.")
                        
                        # Resetar estado do botão
                        st.session_state["remover_subempresa_clicked"] = False


