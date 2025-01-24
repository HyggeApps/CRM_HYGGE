import streamlit as st
from utils.database import get_collection

def gerenciamento_contatos(user):
    collection_contatos = get_collection("contatos")
    collection_empresas = get_collection("empresas")  # Coleção de Empresas Matriz
    collection_subempresas = get_collection("subempresas")  # Coleção de SubEmpresas

    # Abas para Gerenciamento de Contatos
    tab1, tab2, tab3, tab4 = st.tabs(["Contatos cadastrados", "Editar contato", "Cadastrar contato", "Remover contato"])

    # -------------------
    # Aba: Exibir Contatos
    # -------------------
    with tab1:
        st.header("Contatos Vinculados às Empresas/SubEmpresas do Usuário")
        st.info("Visualize os contatos vinculados às empresas ou subempresas cadastradas por você.")
        st.write("---")

        # Obter CNPJs das empresas e subempresas cadastradas pelo usuário
        empresas_cadastradas = list(collection_empresas.find({"usuario": user}, {"_id": 0, "cnpj": 1}))
        subempresas_cadastradas = list(collection_subempresas.find({"usuario": user}, {"_id": 0, "cnpj": 1}))

        # Combinar CNPJs das empresas e subempresas
        cnpjs_usuario = [e["cnpj"] for e in empresas_cadastradas] + [s["cnpj"] for s in subempresas_cadastradas]

        # Filtrar contatos vinculados aos CNPJs do usuário
        contatos_filtrados = list(collection_contatos.find({"empresa": {"$in": cnpjs_usuario}}, {"_id": 0}))

        if contatos_filtrados:
            import pandas as pd

            # Converter para DataFrame
            df_contatos = pd.DataFrame(contatos_filtrados)
            df_contatos = df_contatos.rename(
                columns={
                    "nome": "Nome",
                    "sobrenome": "Sobrenome",
                    "email": "Email",
                    "fone": "Telefone",
                    "linkedin": "LinkedIn",
                    "setor": "Setor",
                    "empresa": "CNPJ Vinculado",
                    "tipo_empresa": "Tipo de Entidade",
                }
            )

            # Exibir tabela de contatos
            st.dataframe(df_contatos, use_container_width=True)
        else:
            st.warning("Nenhum contato encontrado para as empresas ou subempresas cadastradas por você.")

    # -------------------
    # Aba: Editar Contatos
    # -------------------
    with tab2:
        st.header("Editar Contatos")
        st.write(1)
        st.info("Selecione um contato para editar suas informações.")
        st.write("---")

        # Filtrar contatos vinculados aos CNPJs do usuário
        contatos_filtrados = list(collection_contatos.find({"empresa": {"$in": cnpjs_usuario}}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))

        # Criar opções para o selectbox
        opcoes_contatos = [f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos_filtrados]

        if not contatos_filtrados:
            st.warning("Nenhum contato disponível para edição.")
        else:
            contato_selecionado = st.selectbox("Selecione o Contato para Editar", options=opcoes_contatos, key="contato_editar")

            if contato_selecionado:
                # Obter email do contato selecionado
                email_editar = contato_selecionado.split("(")[-1].strip(")")

                # Obter dados do contato
                contato_dados = collection_contatos.find_one({"email": email_editar}, {"_id": 0})

                if contato_dados:
                    with st.form(key="form_editar_contato"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nome = st.text_input("Nome", value=contato_dados.get("nome", ""), key="edit_nome")
                        with col2:
                            sobrenome = st.text_input("Sobrenome", value=contato_dados.get("sobrenome", ""), key="edit_sobrenome")

                        col3, col4 = st.columns(2)
                        with col3:
                            email = st.text_input("Email", value=contato_dados.get("email", ""), disabled=True, key="edit_email")
                        with col4:
                            fone = st.text_input("Telefone", value=contato_dados.get("fone", ""), key="edit_fone")

                        col5, col6 = st.columns(2)
                        with col5:
                            linkedin = st.text_input("LinkedIn", value=contato_dados.get("linkedin", ""), key="edit_linkedin")
                        with col6:
                            setor = st.text_input("Setor", value=contato_dados.get("setor", ""), key="edit_setor")

                        submit_editar = st.form_submit_button("Salvar Alterações")

                        if submit_editar:
                            # Atualizar os dados no banco de dados
                            document_update = {
                                "nome": nome,
                                "sobrenome": sobrenome,
                                "fone": fone,
                                "linkedin": linkedin,
                                "setor": setor,
                            }
                            collection_contatos.update_one({"email": email_editar}, {"$set": document_update})
                            st.success("Contato atualizado com sucesso!")


    # Aba: Cadastrar Contato
    with tab3:
        st.header("Cadastrar Contato")

        # Obter empresas e subempresas cadastradas
        empresas = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        subempresas = list(collection_subempresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))

        # Combinar empresas e subempresas para o selectbox
        entidades = [{"nome": e["razao_social"], "cnpj": e["cnpj"], "tipo": "Empresa"} for e in empresas]
        entidades += [{"nome": s["razao_social"], "cnpj": s["cnpj"], "tipo": "SubEmpresa"} for s in subempresas]

        opcoes_entidades = ['']+[f"{e['nome']} (CNPJ: {e['cnpj']}) [{e['tipo']}]" for e in entidades]
        
        if not entidades:
            st.warning("Nenhuma empresa ou subempresa encontrada. Cadastre uma empresa ou subempresa antes de adicionar contatos.")
        else:
            empresa = st.selectbox("Empresa ou SubEmpresa Associada", options=opcoes_entidades, key="select_empresa_contato")
            if empresa != '':
                with st.form(key="form_cadastro_contato"):
                    nome = st.text_input("Nome do Contato", key="input_nome_contato")
                    sobrenome = st.text_input("Sobrenome do Contato", key="input_sobrenome_contato")
                    email = st.text_input("Email", key="input_email_contato")
                    fone = st.text_input("Telefone", key="input_fone_contato")
                    linkedin = st.text_input("LinkedIn", key="input_linkedin_contato")
                    setor = st.text_input("Setor", key="input_setor_contato")

                    submit = st.form_submit_button("Cadastrar")

                    if submit:
                        if nome and email and empresa:
                            # Obter a entidade selecionada (empresa ou subempresa)
                            entidade_selecionada = next((e for e in entidades if f"{e['nome']} (CNPJ: {e['cnpj']}) [{e['tipo']}]" == empresa), None)
                            if entidade_selecionada:
                                # Criar o documento do contato
                                document = {
                                    "nome": nome,
                                    "sobrenome": sobrenome,
                                    "email": email,
                                    "fone": fone,
                                    "linkedin": linkedin,
                                    "setor": setor,
                                    "empresa": entidade_selecionada["cnpj"],  # Associar ao CNPJ da entidade
                                    "tipo_empresa": entidade_selecionada["tipo"],  # Indicar se é empresa ou subempresa
                                }
                                collection_contatos.insert_one(document)
                                st.success("Contato cadastrado com sucesso!")
                            else:
                                st.error("Erro ao localizar a empresa ou subempresa selecionada. Por favor, tente novamente.")
                        else:
                            st.error("Preencha todos os campos obrigatórios (Nome, Email, Empresa/SubEmpresa).")

    # Aba: Remover Contato
    with tab4:
        st.header("Remover Contato")
        with st.form(key="form_remover_contato"):
            remove_email = st.text_input("Email do Contato a Remover", key="input_remover_email_contato")
            remove_submit = st.form_submit_button("Remover Contato")

            if remove_submit:
                if remove_email:
                    # Verificar se o contato existe e remover
                    result = collection_contatos.delete_one({"email": remove_email})
                    if result.deleted_count > 0:
                        st.success(f"Contato com Email '{remove_email}' removido com sucesso!")
                    else:
                        st.error(f"Nenhum contato encontrado com o Email '{remove_email}'.")
                else:
                    st.error("Por favor, insira o Email do contato para remover.")