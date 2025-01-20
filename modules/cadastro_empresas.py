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

def gerenciamento_empresas(user):
    collection_empresas = get_collection("empresas")
    collection_usuarios = get_collection("usuarios")
    collection_subempresas = get_collection("subempresas")

    # Abas para Gerenciamento de Empresas
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Empresas cadastradas","Cadastrar Empresa", "Remover Empresa", "Cadastrar SubEmpresa", "Remover SubEmpresa"])
    


    # -------------------
    # Aba: Exibir Empresas com Filtros
    # -------------------
    with tab1:

        # -------------------
        # Sidebar: Filtros para consulta de empresas
        # -------------------
        st.write('----')
        st.header("Filtro para empresas:")

        # Campos de filtro
        filtro_razao_social = st.text_input("Razão Social (ou parte)", placeholder="Digite parte da Razão Social")
        filtro_cnpj = st.text_input("CNPJ (ou parte)", placeholder="Digite parte do CNPJ")
        filtro_cidade = st.text_input("Cidade", placeholder="Digite a cidade")
        filtro_estado = st.text_input("Estado (UF)", max_chars=2, placeholder="Ex: SP")
        filtro_tamanho = st.multiselect(
            "Tamanho da Empresa",
            options=["Pequena", "Média", "Grande"],
            default=[],
        )

        # Botão para aplicar filtros
        aplicar_filtros = st.button("Aplicar Filtros")
        st.subheader("Empresas Cadastradas na base de dados da HYGGE")
        st.info("Visualize e filtre as empresas cadastradas na nossa base de dados.")

        # Query inicial sem filtros
        query = {}

        # Adicionar condições de filtro à query
        if aplicar_filtros:
            if filtro_razao_social:
                query["razao_social"] = {"$regex": filtro_razao_social, "$options": "i"}  # Busca parcial (case insensitive)
            if filtro_cnpj:
                query["cnpj"] = {"$regex": filtro_cnpj, "$options": "i"}  # Busca parcial (case insensitive)
            if filtro_cidade:
                query["cidade"] = {"$regex": filtro_cidade, "$options": "i"}  # Busca parcial (case insensitive)
            if filtro_estado:
                query["estado"] = filtro_estado.upper()  # Igualdade exata para estado
            if filtro_tamanho:
                query["tamanho_empresa"] = {"$in": filtro_tamanho}  # Filtro múltiplo para tamanhos

        # Buscar as empresas no banco de dados com os filtros aplicados
        empresas_filtradas = list(collection_empresas.find(query, {"_id": 0, "razao_social": 1, "cnpj": 1, "cidade": 1, "estado": 1, "pais": 1, "tamanho_empresa": 1, "usuario": 1}))

        if empresas_filtradas:
            import pandas as pd

            # Converter para DataFrame
            df_empresas = pd.DataFrame(empresas_filtradas)

            # Renomear as colunas
            df_empresas = df_empresas.rename(
                columns={
                    "razao_social": "Razão Social",
                    "cnpj": "CNPJ",
                    "cidade": "Cidade",
                    "estado": "UF",
                    "pais": "País",
                    "tamanho_empresa": "Tamanho",
                    "usuario": "Vendedor"
                }
            )

            # Exibir a tabela
            st.dataframe(df_empresas, use_container_width=True)
        else:
            st.warning("Nenhuma empresa encontrada com os critérios aplicados.")


    # -------------------
    # Aba: Cadastrar Empresa
    # -------------------
    with tab2:
        st.header("Cadastrar nova empresa na base de dados da HYGGE")
        st.info("Busque automaticamente informações da empresa a partir do CNPJ e/ou CEP e preencha os demais campos no formulário abaixo.")
        st.write('---')
        # Variáveis para preenchimento automático
        if "dados_cnpj" not in st.session_state:
            st.session_state["dados_cnpj"] = {}
        if "dados_cep" not in st.session_state:
            st.session_state["dados_cep"] = {}

        # Buscar CNPJ antes de exibir o formulário
        st.subheader("Busca Automática de CNPJ e CEP")
        with st.expander("Preencher Dados com CNPJ e CEP"):
            cnpj_input = st.text_input("CNPJ", max_chars=18, placeholder="Digite o CNPJ (com ou sem formatação)", key="cnpj_input")
            if st.button("Buscar Dados do CNPJ"):
                cnpj_limpo = cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")  # Remove espaços e pontuação
                if len(cnpj_limpo) == 14:  # Verifica se o CNPJ tem 14 dígitos
                    dados_cnpj = buscar_dados_cnpj(cnpj_limpo)
                    if dados_cnpj and not dados_cnpj.get("erro"):
                        st.success("Dados do CNPJ encontrados!")
                        st.session_state["dados_cnpj"] = dados_cnpj  # Salvar no session_state
                    else:
                        st.error("CNPJ não encontrado ou inválido!")
                        st.session_state["dados_cnpj"] = {}
                else:
                    st.error("CNPJ inválido! Certifique-se de que o CNPJ tem 14 dígitos.")

            cep_input = st.text_input("CEP", max_chars=10, placeholder="Digite o CEP (com ou sem formatação)", key="cep_input")
            if st.button("Buscar Dados do CEP"):
                cep_limpo = cep_input.replace("-", "").replace(" ", "")  # Remove espaços e pontuação
                if len(cep_limpo) == 8:  # Verifica se o CEP tem 8 dígitos
                    dados_cep = buscar_dados_cep(cep_limpo)
                    if dados_cep and not dados_cep.get("erro"):
                        st.success("Dados do CEP encontrados!")
                        st.session_state["dados_cep"] = dados_cep  # Salvar no session_state
                    else:
                        st.error("CEP não encontrado ou inválido!")
                        st.session_state["dados_cep"] = {}
                else:
                    st.error("CEP inválido! Certifique-se de que o CEP tem 8 dígitos.")

        # Obter usuários cadastrados
        usuarios = list(collection_usuarios.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))

        if not usuarios:
            st.warning("Nenhum usuário encontrado. Cadastre um usuário primeiro antes de adicionar empresas.")
        else:
            # Formulário principal
            st.subheader("Formulário de cadastro")
            with st.form(key="form_cadastro_empresa"):
                razao_social = st.text_input("Razão Social", value=st.session_state["dados_cnpj"].get("nome", ""), key="razao_social")
                cnpj = st.text_input("CNPJ", value=cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", ""), max_chars=18, key="cnpj")
                rua = st.text_input("Rua", value=st.session_state["dados_cnpj"].get("logradouro", st.session_state["dados_cep"].get("logradouro", "")), key="rua")
                bairro = st.text_input("Bairro", value=st.session_state["dados_cnpj"].get("bairro", st.session_state["dados_cep"].get("bairro", "")), key="bairro")
                cidade = st.text_input("Cidade", value=st.session_state["dados_cnpj"].get("municipio", st.session_state["dados_cep"].get("localidade", "")), key="cidade")
                estado = st.text_input("Estado", value=st.session_state["dados_cnpj"].get("uf", st.session_state["dados_cep"].get("uf", "")), key="estado")
                cep = st.text_input("CEP", value=cep_input, max_chars=10, key="cep")
                site = st.text_input("Site", key="site")
                fone = st.text_input("Telefone", value=st.session_state["dados_cnpj"].get("telefone", ""), key="fone")
                insc_estadual = st.text_input("Inscrição Estadual", key="insc_estadual")
                setor = st.text_input("Setor", key="setor")
                tamanho_empresa = st.selectbox("Tamanho da Empresa", ["Pequena", "Média", "Grande"], key="tamanho_empresa")
                submit = st.form_submit_button("Cadastrar")

                if submit:
                    if razao_social and cnpj:
                        # Verificar duplicidade no banco de empresas
                        existing_company = collection_empresas.find_one({"cnpj": cnpj})
                        if existing_company:
                            st.error("Empresa já cadastrada com este CNPJ!")
                        else:

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
                                "usuario": user,
                            }
                            collection_empresas.insert_one(document)
                            st.success("Empresa cadastrada com sucesso!")
                    else:
                        st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ).")


    # -------------------
    # Aba: Remover Empresa
    # -------------------
    with tab3:
        st.subheader("Remover Empresa")
        empresas = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        opcoes_empresas = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas]

        if not empresas:
            st.warning("Nenhuma empresa encontrada para remoção.")
        else:
            with st.form(key="form_remover_empresa"):
                empresa_selecionada = st.selectbox("Selecione a Empresa a Remover", options=opcoes_empresas)
                remove_submit = st.form_submit_button("Remover Empresa")

                if remove_submit:
                    cnpj_remover = empresa_selecionada.split("CNPJ: ")[-1].strip(")")
                    result = collection_empresas.delete_one({"cnpj": cnpj_remover})
                    if result.deleted_count > 0:
                        st.success(f"Empresa com CNPJ '{cnpj_remover}' removida com sucesso!")
                    else:
                        st.error(f"Erro ao remover a empresa com CNPJ '{cnpj_remover}'.")

    # -------------------
    # Aba: Cadastrar SubEmpresa
    # -------------------
    with tab4:
        st.subheader("Cadastrar SubEmpresa")

        # Obter empresas matriz cadastradas
        empresas_matriz = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        opcoes_matriz = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas_matriz]

        if not empresas_matriz:
            st.warning("Nenhuma empresa matriz encontrada. Cadastre uma empresa matriz antes de adicionar subempresas.")
        else:
            # Variáveis para preenchimento automático
            dados_cnpj = {}
            dados_cep = {}

            st.subheader("Busca Automática de CNPJ e CEP")
            with st.expander("Preencher Dados com CNPJ e CEP"):
                # Buscar dados do CNPJ
                cnpj_input = st.text_input("CNPJ da SubEmpresa", max_chars=18, placeholder="Digite o CNPJ (com ou sem formatação)")
                if st.button("Buscar Dados do CNPJ (SubEmpresa)"):
                    cnpj_limpo = cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")  # Limpar formatação
                    if len(cnpj_limpo) == 14:
                        dados_cnpj = buscar_dados_cnpj(cnpj_limpo)
                        if dados_cnpj and not dados_cnpj.get("erro"):
                            st.success("Dados do CNPJ encontrados!")
                        else:
                            st.error("CNPJ não encontrado ou inválido!")
                            dados_cnpj = {}
                    else:
                        st.error("CNPJ inválido! Certifique-se de que o CNPJ tem 14 dígitos.")

                # Buscar dados do CEP
                cep_input = st.text_input("CEP da SubEmpresa", max_chars=10, placeholder="Digite o CEP (com ou sem formatação)")
                if st.button("Buscar Dados do CEP (SubEmpresa)"):
                    cep_limpo = cep_input.replace("-", "").replace(" ", "")  # Limpar formatação
                    if len(cep_limpo) == 8:
                        dados_cep = buscar_dados_cep(cep_limpo)
                        if dados_cep and not dados_cep.get("erro"):
                            st.success("Dados do CEP encontrados!")
                        else:
                            st.error("CEP não encontrado ou inválido!")
                            dados_cep = {}
                    else:
                        st.error("CEP inválido! Certifique-se de que o CEP tem 8 dígitos.")

            # Formulário de Cadastro de SubEmpresa
            with st.form(key="form_cadastro_subempresa"):
                empresa_matriz = st.selectbox("Empresa Matriz", options=opcoes_matriz, key="select_empresa_matriz")
                razao_social = st.text_input("Razão Social da SubEmpresa", value=dados_cnpj.get("nome", ""), key="input_razao_social_subempresa")
                cnpj = st.text_input("CNPJ da SubEmpresa", value=cnpj_input, max_chars=18, key="input_cnpj_subempresa")
                rua = st.text_input("Rua", value=dados_cnpj.get("logradouro", dados_cep.get("logradouro", "")), key="input_rua_subempresa")
                cep = st.text_input("CEP", value=cep_input, max_chars=10, key="input_cep_subempresa")
                bairro = st.text_input("Bairro", value=dados_cnpj.get("bairro", dados_cep.get("bairro", "")), key="input_bairro_subempresa")
                cidade = st.text_input("Cidade", value=dados_cnpj.get("municipio", dados_cep.get("localidade", "")), key="input_cidade_subempresa")
                estado = st.text_input("Estado", value=dados_cnpj.get("uf", dados_cep.get("uf", "")), key="input_estado_subempresa")
                fone = st.text_input("Telefone", value=dados_cnpj.get("telefone", ""), key="input_fone_subempresa")

                submit_sub = st.form_submit_button("Cadastrar SubEmpresa")

                if submit_sub:
                    if razao_social and cnpj and empresa_matriz:
                        matriz_cnpj = empresa_matriz.split("CNPJ: ")[-1].strip(")")
                        existing_subempresa = collection_subempresas.find_one({"cnpj": cnpj})
                        if existing_subempresa:
                            st.error("SubEmpresa já cadastrada com este CNPJ!")
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
                            st.success("SubEmpresa cadastrada e vinculada à matriz com sucesso!")
                    else:
                        st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ, Empresa Matriz).")

    # -------------------
    # Aba: Remover SubEmpresa
    # -------------------
    with tab5:
        st.subheader("Remover SubEmpresa")
        
        # Obter subempresas cadastradas
        subempresas = list(collection_subempresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1, "empresa_matriz": 1}))
        opcoes_subempresas = [f"{s['razao_social']} (CNPJ: {s['cnpj']}) - Matriz: {s['empresa_matriz']}" for s in subempresas]

        if not subempresas:
            st.warning("Nenhuma subempresa encontrada para remoção.")
        else:
            with st.form(key="form_remover_subempresa"):
                # Selecionar subempresa para remoção
                subempresa_selecionada = st.selectbox("Selecione a SubEmpresa a Remover", options=opcoes_subempresas, key="select_remover_subempresa")
                remove_submit = st.form_submit_button("Remover SubEmpresa")

                if remove_submit:
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
                        st.success(f"SubEmpresa com CNPJ '{cnpj_remover}' removida com sucesso e desvinculada da matriz '{empresa_matriz}'!")
                    else:
                        st.error(f"Erro ao remover a subempresa com CNPJ '{cnpj_remover}'.")
