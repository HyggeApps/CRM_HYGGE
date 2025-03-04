import streamlit as st
from utils.database import get_collection

def gerenciamento_produtos():

    collection = get_collection("produtos")

    # Abas para gerenciar produtos
    tab1, tab2, tab3 = st.tabs(["Cadastrar Produto", "Remover Produto", "Exibir Produtos"])

    # Aba: Cadastrar Produto
    with tab1:
        st.subheader("Cadastrar Produto")
        with st.form(key="form_cadastro_produto"):
            nome = st.text_input("Nome do Produto", key="input_nome")
            preco = st.number_input("Preço", min_value=0.0, step=0.01, key="input_preco")
            categoria = st.text_input("Categoria", key="input_categoria")
            descricao = st.text_area("Descrição", key="input_descricao")
            base_desconto = st.number_input("Base de Desconto (%)", min_value=0.0, max_value=100.0, step=0.1, key="input_base_desconto")
            status = st.selectbox("Status", ["Ativo", "Inativo"], key="input_status")

            submit = st.form_submit_button("Cadastrar")

            if submit:
                if nome and preco and categoria and status:
                    # Verificar duplicidade no banco de dados
                    existing_product = collection.find_one({"nome": nome})
                    if existing_product:
                        st.error("Produto já cadastrado com este nome!")
                    else:
                        # Criar o documento
                        document = {
                            "nome": nome,
                            "preco": preco,
                            "categoria": categoria,
                            "descricao": descricao,
                            "base_desconto": base_desconto,
                            "status": status,
                        }
                        collection.insert_one(document)
                        st.success("Produto cadastrado com sucesso!")
                else:
                    st.error("Preencha todos os campos obrigatórios (Nome, Preço, Categoria, Status).")

    # Aba: Remover Produto
    with tab2:
        st.subheader("Remover Produto")
        with st.form(key="form_remover_produto"):
            remove_nome_or_id = st.text_input("Nome ou Produto_ID do Produto a Remover", key="input_remove_nome_or_id")
            remove_submit = st.form_submit_button("Remover Produto")

            if remove_submit:
                if remove_nome_or_id:
                    # Verificar se o produto existe e remover
                    result = collection.delete_one({"$or": [{"nome": remove_nome_or_id}]})
                    if result.deleted_count > 0:
                        st.success(f"Produto '{remove_nome_or_id}' removido com sucesso!")
                    else:
                        st.error(f"Nenhum produto encontrado com Nome/ID '{remove_nome_or_id}'.")
                else:
                    st.error("Por favor, insira o Nome ou Produto_ID do produto para remover.")

    # Aba: Exibir Produtos
    with tab3:
        st.subheader("Produtos Cadastrados")
        produtos = list(collection.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
        if produtos:
            st.write("Lista de Produtos:")
            for produto in produtos:
                st.write(
                    f"Nome: {produto['nome']}, Preço: R${produto['preco']:.2f}, Categoria: {produto['categoria']}, "
                    f"Descrição: {produto['descricao']}, Base de Desconto: {produto['base_desconto']}%, Status: {produto['status']}"
                )
        else:
            st.write("Nenhum produto cadastrado ainda.")