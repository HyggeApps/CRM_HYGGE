import streamlit as st
from utils.database import get_collection

def gerenciamento_empresas():
    st.title("Gerenciamento de Empresas")
    collection_empresas = get_collection("empresas")
    collection_subempresas = get_collection("subempresas")
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
                razao_social = st.text_input("Razão Social", key="input_razao_social")
                cnpj = st.text_input("CNPJ", key="input_cnpj")
                rua = st.text_input("Rua", key="input_rua")
                cep = st.text_input("CEP", key="input_cep")
                bairro = st.text_input("Bairro", key="input_bairro")
                cidade = st.text_input("Cidade", key="input_cidade")
                estado = st.text_input("Estado", key="input_estado")
                pais = st.text_input("País", key="input_pais")
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
                                "pais": pais,
                                "site": site,
                                "fone": fone,
                                "insc_estadual": insc_estadual,
                                "setor": setor,
                                "tamanho_empresa": tamanho_empresa,
                                "usuario": usuario.split("(")[-1].strip(")"),
                                "documentos": documentos_salvos,
                                "subempresas": [],  # Inicializar com lista vazia
                            }
                            collection_empresas.insert_one(document)
                            st.success("Empresa cadastrada com sucesso!")
                    else:
                        st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ).")

    # Aba: Cadastrar SubEmpresa
    with tab2:
        st.header("Cadastrar SubEmpresa")

        # Obter empresas matriz cadastradas
        empresas_matriz = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        opcoes_matriz = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas_matriz]

        if not empresas_matriz:
            st.warning("Nenhuma empresa matriz encontrada. Cadastre uma empresa matriz primeiro antes de adicionar subempresas.")
        else:
            with st.form(key="form_cadastro_subempresa"):
                empresa_matriz = st.selectbox("Empresa Matriz", options=opcoes_matriz, key="select_empresa_matriz")
                razao_social = st.text_input("Razão Social da SubEmpresa", key="input_razao_social_subempresa")
                cnpj = st.text_input("CNPJ da SubEmpresa", key="input_cnpj_subempresa")
                rua = st.text_input("Rua", key="input_rua_subempresa")
                cep = st.text_input("CEP", key="input_cep_subempresa")
                bairro = st.text_input("Bairro", key="input_bairro_subempresa")
                cidade = st.text_input("Cidade", key="input_cidade_subempresa")
                estado = st.text_input("Estado", key="input_estado_subempresa")
                fone = st.text_input("Telefone", key="input_fone_subempresa")

                submit = st.form_submit_button("Cadastrar SubEmpresa")

                if submit:
                    if razao_social and cnpj and empresa_matriz:
                        matriz_selecionada = next((e for e in empresas_matriz if f"{e['razao_social']} (CNPJ: {e['cnpj']})" == empresa_matriz), None)
                        if matriz_selecionada:
                            # Verificar duplicidade no banco de subempresas
                            existing_subempresa = collection_subempresas.find_one({"cnpj": cnpj})
                            if existing_subempresa:
                                st.error("SubEmpresa já cadastrada com este CNPJ!")
                            else:
                                # Criar o documento da subempresa
                                document = {
                                    "empresa_matriz": matriz_selecionada["cnpj"],
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

                                # Atualizar a matriz com a subempresa vinculada
                                collection_empresas.update_one(
                                    {"cnpj": matriz_selecionada["cnpj"]},
                                    {"$push": {"subempresas": cnpj}}
                                )
                                st.success("SubEmpresa cadastrada e vinculada à matriz com sucesso!")
                        else:
                            st.error("Erro ao localizar a empresa matriz selecionada. Por favor, tente novamente.")
                    else:
                        st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ, Empresa Matriz).")

    # Aba: Remover Empresa
    with tab3:
        st.header("Remover Empresa")
        with st.form(key="form_remover_empresa"):
            remove_cnpj = st.text_input("CNPJ da Empresa a Remover", key="input_remover_cnpj")
            remove_submit = st.form_submit_button("Remover Empresa")

            if remove_submit:
                if remove_cnpj:
                    # Verificar se a empresa existe e remover
                    result = collection_empresas.delete_one({"cnpj": remove_cnpj})
                    if result.deleted_count > 0:
                        st.success(f"Empresa com CNPJ '{remove_cnpj}' removida com sucesso!")
                    else:
                        st.error(f"Nenhuma empresa encontrada com o CNPJ '{remove_cnpj}'.")
                else:
                    st.error("Por favor, insira o CNPJ da empresa para remover.")

    # Aba: Exibir Empresas
    with tab4:
        st.header("Empresas Cadastradas")
        if st.button("Carregar Empresas", key="botao_carregar_empresas"):
            empresas = list(collection_empresas.find({}, {"_id": 0}))
            if empresas:
                st.write("Lista de Empresas:")
                for empresa in empresas:
                    st.write(
                        f"Razão Social: {empresa['razao_social']}, CNPJ: {empresa['cnpj']}, "
                        f"SubEmpresas: {empresa.get('subempresas', [])}, "
                        f"Endereço: {empresa['rua']}, {empresa['bairro']}, {empresa['cidade']}, {empresa['estado']}, {empresa['pais']}, "
                        f"Telefone: {empresa['fone']}, Site: {empresa['site']}"
                    )
            else:
                st.write("Nenhuma empresa cadastrada ainda.")