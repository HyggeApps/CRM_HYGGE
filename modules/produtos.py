import streamlit as st
from utils.database import get_collection

import streamlit as st
from utils.database import get_collection

def gerenciamento_produtos():
    collection = get_collection("produtos")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Cadastrar Produto", "Editar Produto", "Remover Produto", "Exibir Produtos"])
    
    # Aba: Cadastrar Produto
    with tab1:
        st.subheader("Cadastrar Produto")
        # Consulta as categorias já cadastradas e adiciona opção para novo valor
        categorias_existentes = collection.distinct("categoria")
        opcoes_categoria = [''] + categorias_existentes + ["-- Novo --"]
        categoria = st.selectbox("Categoria: *", opcoes_categoria)
        if categoria == "-- Novo --":
            categoria = st.text_input("Digite a nova categoria:")
        
        # --- Tipo ---
        # Se já houver uma categoria, consulta os tipos existentes para ela
        tipos_existentes = []
        if categoria:
            tipos_existentes = collection.distinct("tipo", {"categoria": categoria})
        opcoes_tipo = [''] + tipos_existentes + ["-- Novo --"]
        tipo = st.selectbox("Tipo do empreendimento: *", opcoes_tipo)
        if tipo == "-- Novo --":
            tipo = st.text_input("Digite o novo tipo para a categoria escolhida:")
        
        # --- Tamanho/Quantidade ---
        # Consulta os tamanhos existentes para a combinação de categoria e tipo
        tamanhos_existentes = []
        if categoria and tipo:
            tamanhos_existentes = collection.distinct("tamanho", {"categoria": categoria, "tipo": tipo})
        opcoes_tamanho = [''] + tamanhos_existentes + ["-- Novo --"]
        tamanho = st.selectbox("Tamanho/Quantidade: *", opcoes_tamanho)
        if tamanho == "-- Novo --":
            tamanho = st.text_input("Digite o novo tamanho/quantidade para o tipo escolhido:")
        
        # Preços e nome do produto
        preco_modelagem = st.number_input("Preço Modelagem", min_value=0.0, step=0.01, value=150.0)
        preco_servico = st.number_input("Preço Serviço", min_value=0.0, step=0.01, value=200.0)
        nome_gerado = f"{tipo} - {tamanho}" if tipo and tamanho else ""
        nome_produto = st.text_input("Nome do Produto", value=nome_gerado)
        
        submit = st.form_submit_button("Cadastrar Produto")
        if submit:
            if categoria and tipo and tamanho and nome_produto:
                # Verifica se já existe um produto com este nome
                existing = collection.find_one({"nome": nome_produto})
                if existing:
                    st.error("Produto já cadastrado com este nome!")
                else:
                    document = {
                        "nome": nome_produto,
                        "categoria": categoria,
                        "tipo": tipo,
                        "tamanho": tamanho,
                        "preco_modelagem": preco_modelagem,
                        "preco_servico": preco_servico,
                        "servicos_adicionais": {'Reunião': 1000, 'Urgência': 2000, 'Cenário extra': 2500}
                    }
                    collection.insert_one(document)
                    st.success("Produto cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos obrigatórios.")
    
    # Aba: Editar Produto
    with tab2:
        st.subheader("Editar Produto")
        with st.form(key="form_editar_produto"):
            identifier = st.text_input("Informe o Nome ou Produto_ID para editar")
            novo_preco_modelagem = st.number_input("Novo Preço Modelagem", min_value=0.0, step=0.01)
            novo_preco_servico = st.number_input("Novo Preço Serviço", min_value=0.0, step=0.01)
            submit_edit = st.form_submit_button("Atualizar Produto")
            if submit_edit:
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
    
    # Aba: Remover Produto
    with tab3:
        st.subheader("Remover Produto")
        with st.form(key="form_remover_produto"):
            identifier = st.text_input("Informe o Nome ou Produto_ID do produto a remover")
            submit_remove = st.form_submit_button("Remover Produto")
            if submit_remove:
                if identifier:
                    result = collection.delete_one({"$or": [{"nome": identifier}, {"_id": identifier}]})
                    if result.deleted_count > 0:
                        st.success(f"Produto '{identifier}' removido com sucesso!")
                    else:
                        st.error(f"Nenhum produto encontrado com Nome/ID '{identifier}'.")
                else:
                    st.error("Informe o Nome ou Produto_ID do produto para remover.")
    
    # Aba: Exibir Produtos
    with tab4:
        st.subheader("Produtos Cadastrados")
        produtos = list(collection.find({}, {"_id": 0}))
        if produtos:
            for produto in produtos:
                st.write(
                    f"Nome: {produto.get('nome')}, Categoria: {produto.get('categoria')}, Tipo: {produto.get('tipo')}, "
                    f"Tamanho: {produto.get('tamanho')}, Preço Modelagem: R${produto.get('preco_modelagem'):.2f}, "
                    f"Preço Serviço: R${produto.get('preco_servico'):.2f}, Serviços Adicionais: {produto.get('servicos_adicionais')}"
                )
        else:
            st.write("Nenhum produto cadastrado ainda.")
