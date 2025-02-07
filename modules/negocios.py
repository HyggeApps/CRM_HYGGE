import streamlit as st
from utils.database import get_collection

def gerenciamento_oportunidades():
    collection_oportunidades = get_collection("oportunidades")
    collection_clientes = get_collection("empresas")  # Clientes são as empresas cadastradas
    collection_usuarios = get_collection("usuarios")  # Coleção de Usuários
    collection_produtos = get_collection("produtos")  # Coleção de Produtos
    collection_leads = get_collection("leads")  # Coleção de Leads

    # Abas para gerenciar oportunidades
    tab1, tab2, tab3 = st.tabs(["Cadastrar Oportunidade", "Remover Oportunidade", "Exibir Oportunidades"])

    # Estágios pré-definidos
    estagios = ["Frio", "Morno", "Quente", "Aguardando projeto", "Aguardando a assinatura", "Perdido", "Fechado"]

    # Aba: Cadastrar Oportunidade
    with tab1:
        st.header("Cadastrar Oportunidade")

        # Obter dados para listas suspensas
        clientes = list(collection_clientes.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        usuarios = list(collection_usuarios.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))
        produtos = list(collection_produtos.find({}, {"_id": 0, "nome": 1, "categoria": 1}))
        leads = list(collection_leads.find({}, {"_id": 0, "conteudo": 1, "empresa": 1}))

        opcoes_clientes = [f"{c['razao_social']} (CNPJ: {c['cnpj']})" for c in clientes]
        opcoes_usuarios = [f"{u['nome']} {u['sobrenome']} ({u['email']})" for u in usuarios]
        opcoes_produtos = [f"{p['nome']} ({p['categoria']})" for p in produtos]
        opcoes_leads = [f"Lead para {l['empresa']} - {l['conteudo']}" for l in leads]

        if not clientes or not usuarios or not produtos or not leads:
            st.warning("Certifique-se de ter clientes, usuários, produtos e leads cadastrados antes de adicionar oportunidades.")
        else:
            with st.form(key="form_cadastro_oportunidade"):
                cliente = st.selectbox("Cliente", options=opcoes_clientes, key="select_cliente_oportunidade")
                usuario = st.selectbox("Usuário Responsável", options=opcoes_usuarios, key="select_usuario_oportunidade")
                produto = st.selectbox("Produto", options=opcoes_produtos, key="select_produto_oportunidade")
                lead = st.selectbox("Lead Associado", options=opcoes_leads, key="select_lead_oportunidade")
                valor_estimado = st.number_input("Valor Estimado", min_value=0.0, step=100.0, key="input_valor_estimado_oportunidade")
                estagio = st.selectbox("Estágio", options=estagios, key="select_estagio_oportunidade")
                probabilidade = st.slider("Probabilidade de Fechamento (%)", min_value=0, max_value=100, step=5, key="slider_probabilidade_oportunidade")
                data_criacao = st.date_input("Data de Criação", key="input_data_criacao_oportunidade")
                data_fechamento = st.date_input("Data de Fechamento (Prevista)", key="input_data_fechamento_oportunidade")
                documentos = st.file_uploader("Documentos", accept_multiple_files=True, key="input_documentos_oportunidade")

                submit = st.form_submit_button("Cadastrar")

                if submit:
                    if cliente and usuario and produto and lead:
                        # Obter entidades selecionadas
                        cliente_selecionado = next((c for c in clientes if f"{c['razao_social']} (CNPJ: {c['cnpj']})" == cliente), None)
                        usuario_selecionado = next((u for u in usuarios if f"{u['nome']} {u['sobrenome']} ({u['email']})" == usuario), None)
                        produto_selecionado = next((p for p in produtos if f"{p['nome']} ({p['categoria']})" == produto), None)
                        lead_selecionado = next((l for l in leads if f"Lead para {l['empresa']} - {l['conteudo']}" == lead), None)

                        if cliente_selecionado and usuario_selecionado and produto_selecionado and lead_selecionado:
                            # Processar documentos
                            documentos_salvos = []
                            if documentos:
                                for doc in documentos:
                                    documentos_salvos.append({"nome_documento": doc.name, "tipo": doc.type})

                            # Criar o documento da oportunidade
                            document = {
                                "cliente": cliente_selecionado["cnpj"],
                                "usuario": usuario_selecionado["email"],
                                "produto": produto_selecionado["nome"],
                                "lead": lead_selecionado["conteudo"],
                                "valor_estimado": valor_estimado,
                                "estagio": estagio,
                                "probabilidade": probabilidade,
                                "data_criacao": str(data_criacao),
                                "data_fechamento": str(data_fechamento),
                                "documentos": documentos_salvos,
                            }
                            collection_oportunidades.insert_one(document)
                            st.success("Oportunidade cadastrada com sucesso!")
                        else:
                            st.error("Erro ao localizar as entidades selecionadas. Por favor, tente novamente.")
                    else:
                        st.error("Preencha todos os campos obrigatórios.")

    # Aba: Remover Oportunidade
    with tab2:
        st.header("Remover Oportunidade")
        with st.form(key="form_remover_oportunidade"):
            remove_id = st.text_input("ID da Oportunidade a Remover", key="input_remover_oportunidade_id")
            remove_submit = st.form_submit_button("Remover Oportunidade")

            if remove_submit:
                if remove_id:
                    # Remover a oportunidade pelo ID
                    result = collection_oportunidades.delete_one({"_id": remove_id})
                    if result.deleted_count > 0:
                        st.success(f"Oportunidade com ID '{remove_id}' removida com sucesso!")
                    else:
                        st.error(f"Nenhuma oportunidade encontrada com o ID '{remove_id}'.")
                else:
                    st.error("Por favor, insira o ID da oportunidade para remover.")

    # Aba: Exibir Oportunidades
    with tab3:
        st.header("Oportunidades Cadastradas")
        if st.button("Carregar Oportunidades", key="botao_carregar_oportunidades"):
            oportunidades = list(collection_oportunidades.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if oportunidades:
                st.write("Lista de Oportunidades:")
                for oportunidade in oportunidades:
                    st.write(
                        f"Cliente: {oportunidade['cliente']}, Usuário: {oportunidade['usuario']}, Produto: {oportunidade['produto']}, "
                        f"Valor Estimado: R${oportunidade['valor_estimado']:.2f}, Estágio: {oportunidade['estagio']}, "
                        f"Probabilidade: {oportunidade['probabilidade']}%, Data Criação: {oportunidade['data_criacao']}, "
                        f"Data Fechamento: {oportunidade['data_fechamento']}, Lead: {oportunidade['lead']}"
                    )
            else:
                st.write("Nenhuma oportunidade cadastrada ainda.")