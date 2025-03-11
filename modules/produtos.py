import streamlit as st
from utils.database import get_collection
from bson import ObjectId
import pandas as pd


def gerenciamento_produtos():
    collection = get_collection("produtos")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Cadastrar Produto", "Editar Produto", "Remover Produto", "Exibir Produtos"])
    
    with tab1:
        st.subheader("Cadastrar Produto")
        
        # Linha 1: Categoria, Tipo e Tamanho/Quantidade
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categorias_existentes = collection.distinct("categoria")
            opcoes_categoria = [''] + categorias_existentes + ["-- Novo --"]
            categoria = st.selectbox("Categoria: *", opcoes_categoria, key="cad_categoria")
            if categoria == "-- Novo --":
                categoria = st.text_input("Digite a nova categoria:", key="cad_categoria_novo")
        
        with col2:
            tipos_existentes = collection.distinct("tipo", {"categoria": categoria}) if categoria else []
            opcoes_tipo = [''] + tipos_existentes + ["-- Novo --"]
            tipo = st.selectbox("Tipo do empreendimento: *", opcoes_tipo, key="cad_tipo")
            if tipo == "-- Novo --":
                tipo = st.text_input("Digite o novo tipo para a categoria escolhida:", key="cad_tipo_novo")
        
        with col3:
            tamanhos_existentes = collection.distinct("tamanho", {"categoria": categoria, "tipo": tipo}) if categoria and tipo else []
            opcoes_tamanho = [''] + tamanhos_existentes + ["-- Novo --"]
            tamanho = st.selectbox("Tamanho/Quantidade: *", opcoes_tamanho, key="cad_tamanho")
            if tamanho == "-- Novo --":
                tamanho = st.text_input("Digite o novo tamanho/quantidade para o tipo escolhido:", key="cad_tamanho_novo")
        
        # Linha 2: Preços e Nome do Produto
        col4, col5, col6 = st.columns(3)
        with col4:
            preco_modelagem = st.number_input("Preço Modelagem", min_value=0.0, step=0.01, value=150.0, key="cad_preco_modelagem")
        with col5:
            preco_servico = st.number_input("Preço Serviço", min_value=0.0, step=0.01, value=200.0, key="cad_preco_servico")
        with col6:
            nome_gerado = f"{tipo} - {tamanho}" if tipo and tamanho else ""
            nome_produto = st.text_input("Nome do Produto", value=nome_gerado, key="cad_nome")
        
        # Linha 3: Serviços Adicionais
        st.markdown("### Serviços Adicionais")
        servicos_adicionais = {}
        
        # Serviços pré-definidos
        servicos_opcoes = ['Reunião', 'Urgência', 'Cenário extra']
        servicos_selecionados = st.multiselect("Selecione os serviços adicionais desejados", servicos_opcoes, key="cad_servicos")
        for servico in servicos_selecionados:
            valor = st.number_input(f"Valor para {servico}:", min_value=0, step=1, value=0, key=f"valor_{servico}")
            servicos_adicionais[servico] = valor
        
        # Serviços personalizados (vários)
        if "custom_services" not in st.session_state:
            st.session_state.custom_services = []
        
        with st.expander("Adicionar serviços personalizados"):
            if st.button("Adicionar novo serviço personalizado", key="add_custom_service"):
                st.session_state.custom_services.append({"nome": "", "valor": 0})
            
            # Para cada serviço personalizado, cria campos de entrada
            for idx, service in enumerate(st.session_state.custom_services):
                nome_custom = st.text_input(f"Nome do serviço personalizado {idx+1}:", key=f"custom_nome_{idx}")
                valor_custom = st.number_input(f"Valor para o serviço personalizado {idx+1}:", min_value=0, step=1, key=f"custom_valor_{idx}")
                st.session_state.custom_services[idx]["nome"] = nome_custom
                st.session_state.custom_services[idx]["valor"] = valor_custom
                if nome_custom:
                    servicos_adicionais[nome_custom] = valor_custom
        
        # Botão para cadastrar o produto
        if st.button("Cadastrar Produto", key="cad_submit"):
            if categoria and tipo and tamanho and nome_produto:
                # Verifica duplicidade pelo campo "nome"
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
                        "servicos_adicionais": servicos_adicionais
                    }
                    collection.insert_one(document)
                    st.success("Produto cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos obrigatórios.")
    
# --- Aba: Editar Produto (Tabela com st.data_editor) ---
    with tab2:
        st.subheader("Editar Produtos")
        
        # Consulta todos os produtos e converte para DataFrame
        produtos = list(collection.find({}))
        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            df = pd.DataFrame(produtos)
            # Converte a coluna _id para string para exibição
            df['_id'] = df['_id'].astype(str)
            
            # Exibe a tabela editável
            edited_df = st.data_editor(
                "Edite os produtos abaixo:",
                df,
                num_rows="dynamic",
                use_container_width=True
            )
            
            if st.button("Salvar Alterações"):
                for index, row in edited_df.iterrows():
                    # Recupera o _id e converte para ObjectId
                    product_id = ObjectId(row['_id'])
                    # Cria um dicionário com os campos atualizados (exclui _id)
                    update_data = row.to_dict()
                    update_data.pop('_id', None)
                    # Atualiza o documento no banco
                    result = collection.update_one(
                        {"_id": product_id},
                        {"$set": update_data}
                    )
                st.success("Alterações salvas com sucesso!")
    
    # Aba: Remover Produto
    with tab3:
        st.subheader("Remover Produto")
        identifier_remove = st.text_input("Informe o Nome ou Produto_ID do produto a remover", key="remove_identifier")
        if st.button("Remover Produto", key="remove_submit"):
            if identifier_remove:
                result = collection.delete_one({"$or": [{"nome": identifier_remove}, {"_id": identifier_remove}]})
                if result.deleted_count > 0:
                    st.success(f"Produto '{identifier_remove}' removido com sucesso!")
                else:
                    st.error(f"Nenhum produto encontrado com Nome/ID '{identifier_remove}'.")
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
