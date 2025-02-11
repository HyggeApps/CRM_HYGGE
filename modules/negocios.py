import streamlit as st
from utils.database import get_collection
from datetime import datetime
import pandas as pd
import datetime as dt
import calendar

hoje = dt.date.today()  # current date

def filtrar_por_periodo(df, periodo):
    df_filtrado = df.copy()

    if periodo == "Mês atual":
        ano_atual = hoje.year
        mes_atual = hoje.month
        # Primeiro e último dia do mês atual:
        primeiro_dia = dt.date(ano_atual, mes_atual, 1)
        ultimo_dia = dt.date(
            ano_atual, 
            mes_atual, 
            calendar.monthrange(ano_atual, mes_atual)[1]
        )
        df_filtrado = df_filtrado[
            (df_filtrado['data_criacao'].dt.date >= primeiro_dia) &
            (df_filtrado['data_criacao'].dt.date <= ultimo_dia)
        ]

    elif periodo == "Últimos 30 dias":
        limite = hoje - dt.timedelta(days=30)
        df_filtrado = df_filtrado[df_filtrado['data_criacao'].dt.date >= limite]
    
    elif periodo == "Últimos 3 meses":
        limite = hoje - dt.timedelta(days=90)
        df_filtrado = df_filtrado[df_filtrado['data_criacao'].dt.date >= limite]

    elif periodo == "Últimos 6 meses":
        limite = hoje - dt.timedelta(days=180)
        df_filtrado = df_filtrado[df_filtrado['data_criacao'].dt.date >= limite]

    elif periodo == "Último ano":
        limite = hoje - dt.timedelta(days=365)
        df_filtrado = df_filtrado[df_filtrado['data_criacao'].dt.date >= limite]

    else:
        # "Todo o período": não filtra nada
        pass

    return df_filtrado

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
    df_oportunidades['data_criacao'] = pd.to_datetime(df_oportunidades['data_criacao'], errors='coerce')
    df_oportunidades["data_fechamento"] = pd.to_datetime(df_oportunidades["data_fechamento"], errors="coerce")

    # Opções de períodos
    opcoes_periodo = [
        "Mês atual",
        "Últimos 30 dias",
        "Últimos 3 meses",
        "Últimos 6 meses",
        "Último ano",
        "Todo o período"
    ]

    periodo_escolhido = st.selectbox("Filtrar por período de criação:", opcoes_periodo, index=4)
    df_oportunidades_filtrado = filtrar_por_periodo(df_oportunidades, periodo_escolhido)

    # Mapeamento de ícones para cada estágio
    icones_estagios = {
        "Aguardando projeto": "⏳",
        "Frio": "❄️",
        "Morno": "🌥️",
        "Quente": "🔥",
        "Aguardando a assinatura": "✍️"
    }

    css = """
        <style>
            /* Define um tamanho máximo e rolagem para o conteúdo dos expanders */
            div[data-testid="stExpander"] div[role="group"] {
                max-height: 400px;
                overflow-y: auto;
            }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)
    # Criar colunas para exibição por estágio

    estagios_disponiveis = ["Aguardando projeto", "Frio", "Morno", "Quente", "Aguardando a assinatura"]
    colunas_estagios = st.columns(len(estagios_disponiveis))

    # Seção de oportunidades "ativas"
    for i, estagio in enumerate(estagios_disponiveis):
        with colunas_estagios[i]:
            st.subheader(f"{icones_estagios[estagio]} {estagio}")  # Ícone dinâmico
            
            # Filtra as oportunidades daquele estágio
            df_filtrado = df_oportunidades_filtrado[df_oportunidades_filtrado["estagio"] == estagio]
            
            # Calcula o total da categoria
            total_valor = 0
            for _, row_valor in df_filtrado.iterrows():
                valor_str = str(row_valor['valor_estimado']).replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    total_valor += float(valor_str)
                except ValueError:
                    pass
            
            # Mostra o total acima do expander
            st.write(f"💵 **Total: R$ {total_valor:,.2f}**")
            
            # Expander para ver detalhes
            with st.expander("📋 Ver mais..."):
                st.write('----')
                
                if not df_filtrado.empty:
                    for _, row in df_filtrado.iterrows():
                        st.subheader(f"**{row['nome_oportunidade']}**")
                        st.write(f"**💲 {row['valor_estimado']}**")
                        data_formatada = row['data_fechamento'].strftime("%d/%m/%Y")
                        st.write(f"📆 {data_formatada}")

                        # Criar selectbox para alterar o estágio
                        novo_estagio = st.selectbox(
                            "Alterar estágio",
                            options=estagios_disponiveis,
                            index=estagios_disponiveis.index(row['estagio']),
                            key=f"select_{row['nome_oportunidade']}"
                        )

                        # Se o estágio for alterado, atualizar no MongoDB
                        if novo_estagio != row['estagio']:
                            collection_oportunidades.update_one(
                                {"nome_oportunidade": row['nome_oportunidade']},
                                {"$set": {"estagio": novo_estagio}}
                            )
                            st.success(f"Estágio alterado para {novo_estagio}")
                            st.rerun()  # Atualiza a página após a mudança

                            # ──────────────────────────────────────────────────────────────────────────
                            # Exemplo de "editar oportunidade" via expander
                            # ──────────────────────────────────────────────────────────────────────────
                            with st.popover("✏️ Editar oportunidade"):
                                # Aqui você pode permitir editar campos específicos,
                                # como nome, valor estimado, datas, etc.
                                novo_nome = st.text_input("Nome da oportunidade", value=row["nome_oportunidade"])
                                novo_valor = st.text_input("Valor estimado", value=str(row["valor_estimado"]))
                                nova_data_fechamento = st.date_input(
                                    "Data de fechamento",
                                    value=row["data_fechamento"] if isinstance(row["data_fechamento"], dt.date) 
                                                                else dt.date.today()
                                )
                                
                                if st.button("Salvar alterações", key=f"salvar_{row['nome_oportunidade']}"):
                                    # Monta o dicionário de atualização
                                    update_fields = {
                                        "nome_oportunidade": novo_nome,
                                        "valor_estimado": novo_valor,
                                        # Converta date do widget para string, se for o caso
                                        "data_fechamento": nova_data_fechamento.isoformat()
                                    }
                                    # Atualiza no MongoDB
                                    collection_oportunidades.update_one(
                                        {"nome_oportunidade": row['nome_oportunidade']},
                                        {"$set": update_fields}
                                    )
                                    st.success(f"Oportunidade '{novo_nome}' atualizada com sucesso!")
                                    st.rerun()

                        st.write("----")
                else:
                    st.info("Nenhuma oportunidade.")

    # Separador visual
    st.write('----')
    st.header('💸 Negócios encerrados/On-Hold')

    # Seção de oportunidades "encerradas"
    col1, col2, col3 = st.columns(3)
    estagios_encerrados = {
        "Perdido": {"icone": "❌", "titulo": "Perdidas"},
        "On-hold": {"icone": "⏸️", "titulo": "On-Hold"},
        "Fechado": {"icone": "✅", "titulo": "Fechadas"}
    }
    colunas_encerradas = [col1, col2, col3]

    # Iterar sobre os estágios encerrados
    for col, (estagio, info) in zip(colunas_encerradas, estagios_encerrados.items()):
        with col:
            st.subheader(f"{info['icone']} {info['titulo']}")

            # Filtra as oportunidades daquele estágio
            df_filtrado = df_oportunidades_filtrado[df_oportunidades_filtrado["estagio"] == estagio]

            # Calcula o total da categoria
            total_valor = 0
            for _, row_valor in df_filtrado.iterrows():
                valor_str = str(row_valor['valor_estimado']).replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    total_valor += float(valor_str)
                except ValueError:
                    pass

            # Mostra o total acima do expander
            st.write(f"💵 **Total: R$ {total_valor:,.2f}**")

            # Expander para ver detalhes das propostas encerradas
            with st.expander(f"📋 Propostas {info['titulo'].lower()}"):
                st.write('----')
                
                if not df_filtrado.empty:
                    for _, row in df_filtrado.iterrows():
                        st.subheader(f"**{row['nome_oportunidade']}**")
                        st.write(f"**💲 {row['valor_estimado']}**")
                        data_formatada = row['data_fechamento'].strftime("%d/%m/%Y")
                        st.write(f"📆 {data_formatada}")
                        st.write(1)
                        # Criar selectbox para alterar o estágio
                        novo_estagio = st.selectbox(
                            "Alterar estágio",
                            options=list(estagios_encerrados.keys()),
                            index=list(estagios_encerrados.keys()).index(row['estagio']),
                            key=f"select_{row['nome_oportunidade']}_encerrado"
                        )

                        # Se o estágio for alterado, atualizar no MongoDB
                        if novo_estagio != row['estagio']:
                            collection_oportunidades.update_one(
                                {"nome_oportunidade": row['nome_oportunidade']},
                                {"$set": {"estagio": novo_estagio}}
                            )
                            st.success(f"Estágio alterado para {novo_estagio}")
                            st.rerun()  # Atualiza a página após a mudança

                        st.write("---")

                else:
                    st.info(f"Nenhuma oportunidade.")





