import streamlit as st
from utils.database import get_collection

def gerenciamento_empresas():
    st.title("Gerenciamento de Empresas (Matriz)")
    collection_empresas = get_collection("empresas")
    collection_usuarios = get_collection("usuarios")  # Coleção para listar usuários

    # Abas para gerenciar empresas
    tab1, tab2, tab3 = st.tabs(["Cadastrar Empresa", "Remover Empresa", "Exibir Empresas"])

    # Aba: Cadastrar Empresa
    with tab1:
        st.header("Cadastrar Empresa")

        # Obter usuários cadastrados
        usuarios = list(collection_usuarios.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))
        opcoes_usuarios = [f"{u['nome']} {u['sobrenome']} ({u['email']})" for u in usuarios]  # Criar lista de opções no formato solicitado

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
                            # Processar documentos
                            documentos_salvos = []
                            if documentos:
                                for doc in documentos:
                                    documentos_salvos.append({"nome_documento": doc.name, "tipo": doc.type})

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
                                "usuario": usuario,  # Associar ao usuário selecionado no formato Nome Sobrenome (Email)
                                "documentos": documentos_salvos,
                            }
                            collection_empresas.insert_one(document)
                            st.success("Empresa cadastrada com sucesso!")
                    else:
                        st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ).")

    # Aba: Remover Empresa
    with tab2:
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
    with tab3:
        st.header("Empresas Cadastradas")
        if st.button("Carregar Empresas", key="botao_carregar_empresas"):
            empresas = list(collection_empresas.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if empresas:
                st.write("Lista de Empresas:")
                for empresa in empresas:
                    st.write(
                        f"Razão Social: {empresa['razao_social']}, CNPJ: {empresa['cnpj']}, "
                        f"Endereço: {empresa['rua']}, {empresa['bairro']}, {empresa['cidade']}, {empresa['estado']}, {empresa['pais']}, "
                        f"Telefone: {empresa['fone']}, Site: {empresa['site']}, Usuário Associado: {empresa['usuario']}"
                    )
            else:
                st.write("Nenhuma empresa cadastrada ainda.")