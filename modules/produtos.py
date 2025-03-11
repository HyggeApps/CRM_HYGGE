import streamlit as st
from utils.database import get_collection

def gerenciamento_produtos():
    collection = get_collection("produtos")

    tab1, tab2, tab3, tab4 = st.tabs(["Cadastrar Produto", "Editar Produto", "Remover Produto", "Exibir Produtos"])

    # Aba: Cadastrar Produto
    with tab1:
        st.subheader("Cadastrar Produto")
        with st.form(key="form_cadastro_produto"):
            # Obtém as categorias já cadastradas
            categorias_existentes = collection.distinct("categoria")
            categoria = st.selectbox('Categoria: *', [''] + categorias_existentes, key="input_categoria")

            tipo_empreendimento = None
            tamanho_empreendimento = None

            if categoria:
                # Obtém os tipos para a categoria selecionada
                tipos_existentes = collection.distinct("tipo", {"categoria": categoria})
                tipo_empreendimento = st.selectbox('Tipo do empreendimento: *', [''] + tipos_existentes, key="input_tipo")
                if tipo_empreendimento:
                    # Obtém os tamanhos para a combinação de categoria e tipo
                    tamanhos_existentes = collection.distinct("tamanho", {"categoria": categoria, "tipo": tipo_empreendimento})
                    tamanho_empreendimento = st.selectbox('Tamanho: *', [''] + tamanhos_existentes, key="input_tamanho")

            # Inputs para preços
            preco_modelagem = st.number_input("Preço Modelagem", min_value=0.0, step=0.01, key="input_preco_modelagem")
            preco_servico = st.number_input("Preço Serviço", min_value=0.0, step=0.01, key="input_preco_servico")

            # Geração automática do nome do produto (se todos os campos estiverem preenchidos)
            nome_gerado = f"{categoria} - {tipo_empreendimento} - {tamanho_empreendimento}" if categoria and tipo_empreendimento and tamanho_empreendimento else ""
            nome_produto = st.text_input("Nome do Produto", value=nome_gerado, key="input_nome_produto")

            submit_cadastrar = st.form_submit_button("Cadastrar Produto")

            if submit_cadastrar:
                if nome_produto and preco_modelagem is not None and preco_servico is not None and categoria and tipo_empreendimento and tamanho_empreendimento:
                    # Verifica se já existe um produto com este nome
                    existing = collection.find_one({"nome": nome_produto})
                    if existing:
                        st.error("Produto já cadastrado com este nome!")
                    else:
                        document = {
                            "nome": nome_produto,
                            "categoria": categoria,
                            "tipo": tipo_empreendimento,
                            "tamanho": tamanho_empreendimento,
                            "preco_modelagem": preco_modelagem,
                            "preco_servico": preco_servico
                        }
                        collection.insert_one(document)
                        st.success("Produto cadastrado com sucesso!")
                else:
                    st.error("Preencha todos os campos obrigatórios.")

    # As demais abas (Editar, Remover, Exibir) podem permanecer iguais ou serem ajustadas conforme a necessidade
    with tab2:
        st.subheader("Editar Produto")
        with st.form(key="form_editar_produto"):
            identifier = st.text_input("Informe o Nome ou Produto_ID para editar", key="input_edit_identifier")
            novo_preco_modelagem = st.number_input("Novo Preço Modelagem", min_value=0.0, step=0.01, key="input_novo_preco_modelagem")
            novo_preco_servico = st.number_input("Novo Preço Serviço", min_value=0.0, step=0.01, key="input_novo_preco_servico")
            edit_submit = st.form_submit_button("Atualizar Produto")
            if edit_submit:
                if identifier:
                    result = collection.update_one(
                        {"$or": [{"nome": identifier}, {"_id": identifier}]},
                        {"$set": {
                            "preco_modelagem": novo_preco_modelagem,
                            "preco_servico": novo_preco_servico
                        }}
                    )
                    if result.modified_count > 0:
                        st.success(f"Produto '{identifier}' atualizado com sucesso!")
                    else:
                        st.error(f"Nenhum produto encontrado com Nome/ID '{identifier}'.")
                else:
                    st.error("Informe o Nome ou Produto_ID do produto para editar.")

    with tab3:
        st.subheader("Remover Produto")
        with st.form(key="form_remover_produto"):
            remove_identifier = st.text_input("Nome ou Produto_ID do Produto a Remover", key="input_remove_identifier")
            remove_submit = st.form_submit_button("Remover Produto")
            if remove_submit:
                if remove_identifier:
                    result = collection.delete_one({"$or": [{"nome": remove_identifier}, {"_id": remove_identifier}]})
                    if result.deleted_count > 0:
                        st.success(f"Produto '{remove_identifier}' removido com sucesso!")
                    else:
                        st.error(f"Nenhum produto encontrado com Nome/ID '{remove_identifier}'.")
                else:
                    st.error("Por favor, informe o Nome ou Produto_ID do produto para remover.")

    with tab4:
        st.subheader("Produtos Cadastrados")
        produtos = list(collection.find({}, {"_id": 0}))
        if produtos:
            st.write("Lista de Produtos:")
            for produto in produtos:
                st.write(
                    f"Nome: {produto['nome']}, Categoria: {produto['categoria']}, Tipo: {produto['tipo']}, "
                    f"Tamanho: {produto['tamanho']}, Preço Modelagem: R${produto['preco_modelagem']:.2f}, "
                    f"Preço Serviço: R${produto['preco_servico']:.2f}"
                )
        else:
            st.write("Nenhum produto cadastrado ainda.")