import streamlit as st
from utils.database import get_collection
from datetime import datetime

def gerenciamento_oportunidades(user):
    collection_oportunidades = get_collection("oportunidades")
    collection_clientes = get_collection("empresas")  # Clientes são as empresas cadastradas
    collection_usuarios = get_collection("usuarios")  # Coleção de Usuários
    collection_produtos = get_collection("produtos")  # Coleção de Produtos

    # Estágios pré-definidos
    estagios = ["Frio", "Morno", "Quente", "Aguardando projeto", "Aguardando a assinatura", "Perdido", "Fechado"]

    with st.popover('➕ Cadastrar oportunidade'):
        st.header("Cadastrar Oportunidade")
        st.write('----')
        # Obter dados para listas suspensas
        clientes = list(collection_clientes.find({"usuario": user}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        usuarios = list(collection_usuarios.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))
        produtos = list(collection_produtos.find({}, {"_id": 0, "nome": 1, "categoria": 1, "preco": 1, "base_desconto": 1}))

        opcoes_clientes = [f"{c['razao_social']} (CNPJ: {c['cnpj']})" for c in clientes]
        opcoes_produtos = [f"{p['nome']} ({p['categoria']})" for p in produtos]

        if not clientes:
            st.warning("Você ainda não tem clientes cadastrados. Cadastre um cliente antes de criar oportunidades.")
        elif not usuarios or not produtos:
            st.warning("Certifique-se de ter usuários e produtos cadastrados antes de adicionar oportunidades.")
        else:
            with st.form(key="form_cadastro_oportunidade"):
                cliente = st.selectbox("Cliente", options=opcoes_clientes, key="select_cliente_oportunidade")
                nome_opp = st.text_input('Nome da oportunidade',key="nome_oportunidade")
                produto = st.selectbox("Produto", options=opcoes_produtos, key="select_produto_oportunidade")
                valor_estimado = st.text_input("Valor", value='R$ 9.900,00',disabled=True, key="input_valor_estimado_oportunidade")
                estagio = st.selectbox("Estágio", options=estagios, key="select_estagio_oportunidade")
                data_fechamento = st.date_input("Data de Fechamento (Prevista)", key="input_data_fechamento_oportunidade")
                submit = st.form_submit_button("Cadastrar")

                if submit:
                    if cliente and produto:
                        # Obter entidades selecionadas
                        cliente_selecionado = next((c for c in clientes if f"{c['razao_social']} (CNPJ: {c['cnpj']})" == cliente), None)
                        usuario_selecionado = next((u for u in usuarios if f"{u['nome']} {u['sobrenome']} ({u['email']})" == user), None)
                        produto_selecionado = next((p for p in produtos if f"{p['nome']} ({p['categoria']})" == produto), None)

                        if cliente_selecionado and usuario_selecionado and produto_selecionado:
                            data_hoje = datetime.now().strftime("%Y-%m-%d")  # Data atual
                            # Criar o documento da oportunidade
                            document = {
                                "cliente": cliente_selecionado["cnpj"],
                                "nome_oportunidade": nome_opp,
                                "usuario": user,
                                "produto": produto_selecionado["nome"],
                                "valor_estimado": valor_estimado,
                                "estagio": estagio,
                                "data_criacao": data_hoje,
                                "data_fechamento": str(data_fechamento)
                            }
                            collection_oportunidades.insert_one(document)
                            st.success("Oportunidade cadastrada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao localizar as entidades selecionadas. Por favor, tente novamente.")
                    else:
                        st.error("Preencha todos os campos obrigatórios.")
    st.selectbox('Período',['Todo o período','Último ano', 'Últimos semestre','Ultimo trimestre', 'Ultimo mês'], index=1) 
    st.write('----')
    # Criar cinco colunas para os estágios das oportunidades
    col1, col2, col3, col4, col5 = st.columns(5)

    # Coluna 1 - Frias
    with col1:
        st.subheader('🧊 Frias')
        with st.expander('Propostas frias'):
            st.info('...')
        st.subheader('💵 **Total: R$ 567.901,01**')

    # Coluna 2 - Mornas
    with col2:
        st.subheader('🌥️ Mornas')
        with st.expander('Propostas mornas'):
            st.info('...')
        st.subheader('💵 **Total: R$ 567.901,01**')

    # Coluna 3 - Quentes
    with col3:
        st.subheader('🔥 Quentes')
        with st.expander('Propostas quentes'):
            st.info('...')
        st.subheader('💵 **Total: R$ 567.901,01**')

    # Coluna 4 - Aguardando projeto
    with col4:
        st.subheader('📃 Aguardando projeto')
        with st.expander('Propostas aguardando projeto'):
            st.info('...')
        st.subheader('💵 **Total: R$ 567.901,01**')

    # Coluna 5 - Aguardando assinatura
    with col5:
        st.subheader('✒️ Aguardando assinatura')
        with st.expander('Proposta aguardando assinatura'):
            st.info('...')
        st.subheader('💵 **Total: R$ 567.901,01**')

    st.write('----')


    st.header('💸 Negócios encerrados')
    # Criar duas colunas para organização
    col1, col2 = st.columns(2)

    # Coluna da esquerda - Propostas Fechadas
    with col1:
        st.subheader('✅ Fechadas')
        with st.expander('Propostas fechadas'):
            st.info('...')
        st.subheader('💵 **Total: R$ 567.901,01**')

    # Linha divisória entre colunas
    st.write('----')

    # Coluna da direita - Propostas Perdidas
    with col2:
        st.subheader('❌ Perdidas')
        with st.expander('Propostas perdidas'):
            st.info('...')
        st.subheader('💵 **Total: R$ 567.901,01**')
    
