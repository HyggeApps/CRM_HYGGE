import streamlit as st
from utils.database import get_collection
import pandas as pd
from datetime import datetime, timedelta

def exibir_atividades_empresa(user, admin, empresa_cnpj):
    collection_atividades = get_collection("atividades")
    collection_contatos = get_collection("contatos")

    # Buscar contatos vinculados à empresa
    contatos_vinculados = list(collection_contatos.find({"empresa": empresa_cnpj}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))

    # Criar lista de contatos formatada
    lista_contatos = [""] + [f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos_vinculados]

    # Buscar atividades vinculadas à empresa selecionada
    atividades = list(collection_atividades.find({"empresa": empresa_cnpj}, {"_id": 0}))

    with st.expander("📌 Tarefas/Atividades", expanded=True):
        if atividades:
            df_atividades = pd.DataFrame(atividades)

            # Renomear colunas para exibição
            df_atividades = df_atividades.rename(
                columns={
                    "atividade_id": "ID",
                    "tipo_atividade": "Tipo",
                    "titulo": "Título",
                    "contato": "Contato",
                    "descricao": "Descrição",
                    "data_execucao_atividade": "Data Execução",
                    "data_retorno_atividade": "Data Retorno",
                    "data_criacao_atividade": "Criado em"
                }
            )

            df_atividades = df_atividades[["Data Execução", "Tipo", "Título","Descrição", "Contato"]]

            st.dataframe(df_atividades, hide_index=True, use_container_width=True)
        else:
            st.warning("Nenhuma atividade cadastrada para esta empresa.")

        # Verifica permissão para editar ou adicionar atividades
        if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):

            # Popover para adicionar nova atividade
            with st.popover('➕ Adicionar Atividade'):
                st.write(1)
                with st.form("form_adicionar_atividade"):
                    st.subheader("➕ Nova Atividade")
                    tipo = st.selectbox("Tipo de Atividade *", ["Whatsapp", "Ligação", "Email", "Linkedin", "Reunião"])
                    if tipo == 'Ligação':
                        status = st.selectbox("Status *",['Ocupado',"Conectado","Gatekeeper","Ligação Positiva","Ligação Negativa"])
                    titulo = st.text_input("Título *")
                    contato = st.selectbox("Contato Vinculado *", lista_contatos)  # Mostra apenas os contatos da empresa
                    descricao = st.text_area("Descrição *")

                    # Definir data de criação como hoje
                    data_criacao = datetime.today().date()
                    # Criar campo de data de execução com sugestão
                    data_execucao = st.date_input("Data de Execução", value=data_criacao)

                    submit_atividade = st.form_submit_button("✅ Adicionar Atividade")

                    if submit_atividade:
                        if titulo and tipo and descricao and contatos_vinculados:
                            if tipo != "Ligação": status = 'NA'
                            atividade_id = str(datetime.now().timestamp())  # Gerar um ID único baseado no tempo
                            nova_atividade = {
                                "atividade_id": atividade_id,
                                "tipo_atividade": tipo,
                                "status": status,
                                "titulo": titulo,
                                "empresa": empresa_cnpj,
                                "contato": contato,
                                "descricao": descricao,
                                "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
                                "data_criacao_atividade": datetime.now().strftime("%Y-%m-%d")
                            }
                            collection_atividades.insert_one(nova_atividade)
                            st.success("Atividade adicionada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Preencha os campos obrigatórios: Tipo, Título, Contato, Descrição e Datas.")
