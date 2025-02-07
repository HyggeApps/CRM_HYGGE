import streamlit as st
from utils.database import get_collection
from datetime import datetime
import pandas as pd

def gerenciamento_oportunidades(user):
    collection_oportunidades = get_collection("oportunidades")
    collection_clientes = get_collection("empresas")
    collection_usuarios = get_collection("usuarios")
    collection_produtos = get_collection("produtos")

    estagios = ["Frio", "Morno", "Quente", "Aguardando projeto", "Aguardando a assinatura","On-hold", "Perdido", "Fechado"]

    with st.popover('➕ Cadastrar oportunidade'):
        st.header("Cadastrar Oportunidade")
        st.write('----')
        
        clientes = list(collection_clientes.find({"usuario": user}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        usuarios = list(collection_usuarios.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))
        produtos = list(collection_produtos.find({}, {"_id": 0, "nome": 1, "categoria": 1, "preco": 1, "base_desconto": 1}))

        opcoes_clientes = [f"{c['razao_social']} (CNPJ: {c['cnpj']})" for c in clientes]
        opcoes_produtos = [f"{p['nome']} ({p['categoria']})" for p in produtos]

        if not clientes:
            st.warning("Cadastre um cliente antes de criar oportunidades.")
        elif not usuarios or not produtos:
            st.warning("Certifique-se de ter usuários e produtos cadastrados.")
        else:
            with st.form(key="form_cadastro_oportunidade"):
                cliente = st.selectbox("Cliente", options=opcoes_clientes, key="select_cliente_oportunidade")
                nome_opp = st.text_input('Nome da oportunidade', key="nome_oportunidade")
                produto = st.selectbox("Produto", options=opcoes_produtos, key="select_produto_oportunidade")
                valor_estimado = st.text_input("Valor", value='R$ 9.900,00', disabled=True, key="input_valor_estimado_oportunidade")
                estagio = st.selectbox("Estágio", options=estagios, key="select_estagio_oportunidade")
                data_fechamento = st.date_input("Data de Fechamento (Prevista)", key="input_data_fechamento_oportunidade")
                submit = st.form_submit_button("Cadastrar")

                if submit:
                    if cliente and produto:
                        cliente_selecionado = next((c for c in clientes if f"{c['razao_social']} (CNPJ: {c['cnpj']})" == cliente), None)
                        produto_selecionado = next((p for p in produtos if f"{p['nome']} ({p['categoria']})" == produto), None)

                        if cliente_selecionado and produto_selecionado:
                            data_hoje = datetime.now().strftime("%Y-%m-%d")
                            document = {
                                "cliente": cliente_selecionado["razao_social"],
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
                            st.error("Erro ao localizar as entidades selecionadas. Tente novamente.")
                    else:
                        st.error("Preencha todos os campos obrigatórios.")

    # Buscar oportunidades no banco
    oportunidades = list(collection_oportunidades.find({}, {"_id": 0, "cliente": 1, "nome_oportunidade": 1, "valor_estimado": 1,"data_criacao": 1, "data_fechamento": 1, "estagio": 1}))
    df_oportunidades = pd.DataFrame(oportunidades)

    # Mapeamento de ícones para cada estágio
    icones_estagios = {
        "Frio": "🧊",
        "Morno": "🌥️",
        "Quente": "🔥",
        "Aguardando projeto": "📃",
        "Aguardando a assinatura": "✒️",
        "Fechado": "✅",
        "Perdido": "❌"
    }

    # Criar colunas para exibição por estágio
    colunas_estagios = st.columns(5)
    estagios_disponiveis = ["Aguardando projeto", "Frio", "Morno", "Quente", "Aguardando a assinatura"]

    for i, estagio in enumerate(estagios_disponiveis):
        with colunas_estagios[i]:
            st.subheader(f"{icones_estagios[estagio]} {estagio}")  # Ícone dinâmico
            with st.expander(f"📋 Ver mais..."):
                st.write('----')
                df_filtrado = df_oportunidades[df_oportunidades["estagio"] == estagio]
                
                if not df_filtrado.empty:
                    total_valor = 0  # Inicializa o somatório
                    
                    for _, row in df_filtrado.iterrows():
                        st.subheader(f"**{row['nome_oportunidade']}**")
                        st.write(f"**💲 {row['valor_estimado']}**")
                        st.write(f"📆 {row['data_fechamento']}")
                        st.write("----")

                        # Converter valor para número e somar
                        valor_str = str(row['valor_estimado']).replace("R$", "").replace(".", "").replace(",", ".").strip()
                        try:
                            total_valor += float(valor_str)
                        except ValueError:
                            pass  # Evita erro caso algum valor não seja convertível
                        
                    # Exibir total da categoria
                    st.subheader(f"💵 **Total: R$ {total_valor:,.2f}**")
                else:
                    st.info("Nenhuma oportunidade.")


    st.write('----')
    st.header('💸 Negócios encerrados')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('❌ Perdidas')
        with st.expander("📋 Propostas perdidas"):
            st.write('----')
            df_perdidas = df_oportunidades[df_oportunidades["estagio"] == "Perdido"]

            if not df_perdidas.empty:
                total_valor_perdidas = 0  # Inicializa o somatório
                
                for _, row in df_perdidas.iterrows():
                    st.subheader(f"**{row['nome_oportunidade']}**")
                    st.write(f"**💲 {row['valor_estimado']}**")
                    st.write(f"📆 {row['data_criacao']}")
                    st.write("---")

                    # Conversão do valor para somar corretamente
                    valor_str = str(row['valor_estimado']).replace("R$", "").replace(".", "").replace(",", ".").strip()
                    try:
                        total_valor_perdidas += float(valor_str)
                    except ValueError:
                        pass  # Se não for possível converter, ignora

                # Exibir total da categoria
                st.subheader(f"💵 **Total: R$ {total_valor_perdidas:,.2f}**")
            else:
                st.info("Nenhuma oportunidade perdida.")

    with col2:
        st.subheader('⏸️ On-Hold')
        with st.expander("📋 Propostas on-hold"):
            st.write('----')
            df_onhold = df_oportunidades[df_oportunidades["estagio"] == "On-hold"]

            if not df_onhold.empty:
                total_valor_onhold = 0  # Inicializa o somatório
                
                for _, row in df_onhold.iterrows():
                    st.subheader(f"**{row['nome_oportunidade']}**")
                    st.write(f"**💲 {row['valor_estimado']}**")
                    st.write(f"📆 {row['data_criacao']}")
                    st.write("---")

                    # Conversão do valor para somar corretamente
                    valor_str = str(row['valor_estimado']).replace("R$", "").replace(".", "").replace(",", ".").strip()
                    try:
                        total_valor_onhold += float(valor_str)
                    except ValueError:
                        pass  # Se não for possível converter, ignora

                # Exibir total da categoria
                st.subheader(f"💵 **Total: R$ {total_valor_onhold:,.2f}**")
            else:
                st.info("Nenhuma oportunidade on-hold.")

    with col3:
        st.subheader('✅ Fechadas')
        with st.expander("📋 Propostas fechadas"):
            st.write('----')
            df_fechadas = df_oportunidades[df_oportunidades["estagio"] == "Fechado"]

            if not df_fechadas.empty:
                total_valor_fechadas = 0  # Inicializa o somatório
                
                for _, row in df_fechadas.iterrows():
                    st.subheader(f"**{row['nome_oportunidade']}**")
                    st.write(f"**💲 {row['valor_estimado']}**")
                    st.write(f"📆 {row['data_criacao']}")
                    st.write("---")

                    # Conversão do valor para somar corretamente
                    valor_str = str(row['valor_estimado']).replace("R$", "").replace(".", "").replace(",", ".").strip()
                    try:
                        total_valor_fechadas += float(valor_str)
                    except ValueError:
                        pass  # Se não for possível converter, ignora

                # Exibir total da categoria
                st.subheader(f"💵 **Total: R$ {total_valor_fechadas:,.2f}**")
            else:
                st.info("Nenhuma oportunidade fechada.")


