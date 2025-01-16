import streamlit as st
from utils.database import get_collection

def gerenciamento_contatos():
    st.title("Gerenciamento de Contatos")
    collection_contatos = get_collection("contatos")
    collection_empresas = get_collection("empresas")  # Coleção de Empresas Matriz
    collection_subempresas = get_collection("subempresas")  # Coleção de SubEmpresas

    # Abas para gerenciar contatos
    tab1, tab2, tab3 = st.tabs(["Cadastrar Contato", "Remover Contato", "Exibir Contatos"])

    # Aba: Cadastrar Contato
    with tab1:
        st.header("Cadastrar Contato")

        # Obter empresas e subempresas cadastradas
        empresas = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        subempresas = list(collection_subempresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))

        # Combinar empresas e subempresas para o selectbox
        entidades = [{"nome": e["razao_social"], "cnpj": e["cnpj"], "tipo": "Empresa"} for e in empresas]
        entidades += [{"nome": s["razao_social"], "cnpj": s["cnpj"], "tipo": "SubEmpresa"} for s in subempresas]

        opcoes_entidades = [f"{e['nome']} (CNPJ: {e['cnpj']}) [{e['tipo']}]" for e in entidades]

        if not entidades:
            st.warning("Nenhuma empresa ou subempresa encontrada. Cadastre uma empresa ou subempresa antes de adicionar contatos.")
        else:
            with st.form(key="form_cadastro_contato"):
                nome = st.text_input("Nome do Contato", key="input_nome_contato")
                sobrenome = st.text_input("Sobrenome do Contato", key="input_sobrenome_contato")
                email = st.text_input("Email", key="input_email_contato")
                fone = st.text_input("Telefone", key="input_fone_contato")
                linkedin = st.text_input("LinkedIn", key="input_linkedin_contato")
                setor = st.text_input("Setor", key="input_setor_contato")
                empresa = st.selectbox("Empresa ou SubEmpresa Associada", options=opcoes_entidades, key="select_empresa_contato")

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
    with tab2:
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

    # Aba: Exibir Contatos
    with tab3:
        st.header("Contatos Cadastrados")
        if st.button("Carregar Contatos", key="botao_carregar_contatos"):
            contatos = list(collection_contatos.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if contatos:
                st.write("Lista de Contatos:")
                for contato in contatos:
                    st.write(
                        f"Nome: {contato['nome']} {contato['sobrenome']}, Email: {contato['email']}, "
                        f"Telefone: {contato['fone']}, LinkedIn: {contato['linkedin']}, "
                        f"Setor: {contato['setor']}, Vinculado a: {contato['empresa']} [{contato['tipo_empresa']}]"
                    )
            else:
                st.write("Nenhum contato cadastrado ainda.")
