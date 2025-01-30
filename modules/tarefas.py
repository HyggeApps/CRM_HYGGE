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
                    "observacoes": "Observações",
                    "descricao": "Descrição",
                    "data_execucao_atividade": "Data Execução",
                    "data_retorno_atividade": "Data Retorno",
                    "data_criacao_atividade": "Criado em"
                }
            )

            df_atividades = df_atividades[["ID", "Tipo", "Título", "Contato", "Observações",
                                           "Descrição", "Data Execução", "Data Retorno", "Criado em"]]

            st.dataframe(df_atividades, hide_index=True, use_container_width=True)
        else:
            st.warning("Nenhuma atividade cadastrada para esta empresa.")

        # Verifica permissão para editar ou adicionar atividades
        if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):

            # Popover para adicionar nova atividade
            with st.popover('➕ Adicionar Atividade'):
                with st.form("form_adicionar_atividade"):
                    st.subheader("➕ Nova Atividade")
                    tipo = st.selectbox("Tipo de Atividade *", ["Contato inicial", "Whatsapp", "Ligação", "Email", "Linkedin", "Tarefa", "Reunião", "Blacklist"])
                    titulo = st.text_input("Título *")
                    contato = st.selectbox("Contato Vinculado *", lista_contatos)  # Mostra apenas os contatos da empresa
                    observacoes = st.text_area("Observações")
                    descricao = st.text_area("Descrição *")

                    # Definir data de criação como hoje
                    data_criacao = datetime.today().date()
                    # Sugerir execução 7 dias após a criação
                    data_execucao_sugerida = data_criacao + timedelta(days=3)
                    # Criar campo de data de execução com sugestão
                    data_execucao = st.date_input("Data de Execução *", value=None)
                    # Data de retorno opcional, sugerindo 7 dias após a execução
                    data_retorno = st.date_input("Data de Retorno *", value=None)

                    submit_atividade = st.form_submit_button("✅ Adicionar Atividade")

                    if submit_atividade:
                        if titulo and tipo and descricao and contatos_vinculados and data_execucao and data_retorno:
                            atividade_id = str(datetime.now().timestamp())  # Gerar um ID único baseado no tempo
                            nova_atividade = {
                                "atividade_id": atividade_id,
                                "tipo_atividade": tipo,
                                "titulo": titulo,
                                "empresa": empresa_cnpj,
                                "contato": contato,
                                "observacoes": observacoes,
                                "descricao": descricao,
                                "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
                                "data_retorno_atividade": data_retorno.strftime("%Y-%m-%d") if data_retorno else None,
                                "data_criacao_atividade": datetime.now().strftime("%Y-%m-%d")
                            }
                            collection_atividades.insert_one(nova_atividade)
                            st.success("Atividade adicionada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Preencha os campos obrigatórios: Tipo, Título, Contato, Descrição e Datas.")

            # Se houver atividades cadastradas, exibir popover de edição/remoção
            if atividades:
                with st.popover('✏️ Editar Atividade'):
                    atividade_selecionada = st.selectbox(
                        "Selecione uma atividade para editar/remover",
                        options=[f"{a['titulo']} - {a['data_execucao_atividade']}" for a in atividades]
                    )

                    if atividade_selecionada:
                        titulo_editar = atividade_selecionada.split(" - ")[0]  # Obter título
                        atividade_dados = collection_atividades.find_one({"titulo": titulo_editar}, {"_id": 0})

                        if atividade_dados:
                            with st.form("form_editar_atividade"):
                                st.subheader("✏️ Editar Atividade")
                                novo_tipo = st.selectbox("Tipo de Atividade", ["Contato inicial", "Whatsapp", "Ligação", "Email", "Linkedin", "Tarefa", "Reunião", "Blacklist"],
                                                         index=["Contato inicial", "Whatsapp", "Ligação", "Email", "Linkedin", "Tarefa", "Reunião", "Blacklist"].index(atividade_dados["tipo_atividade"]))
                                novo_titulo = st.text_input("Título", value=atividade_dados["titulo"])
                                novo_contato = st.selectbox("Contato Vinculado", lista_contatos, index=lista_contatos.index(atividade_dados["contato"]) if atividade_dados["contato"] in lista_contatos else 0)
                                novas_observacoes = st.text_area("Observações", value=atividade_dados["observacoes"])
                                nova_descricao = st.text_area("Descrição", value=atividade_dados["descricao"])
                                nova_data_execucao = st.date_input("Data de Execução",
                                                                   value=pd.to_datetime(atividade_dados["data_execucao_atividade"]).date())
                                nova_data_retorno = st.date_input("Data de Retorno",
                                                                  value=pd.to_datetime(atividade_dados["data_retorno_atividade"]).date() if atividade_dados["data_retorno_atividade"] else None)

                                submit_editar = st.form_submit_button("💾 Salvar Alterações")
                                if submit_editar:
                                    collection_atividades.update_one(
                                        {"atividade_id": atividade_dados["atividade_id"]},
                                        {"$set": {
                                            "tipo_atividade": novo_tipo,
                                            "titulo": novo_titulo,
                                            "contato": novo_contato,
                                            "observacoes": novas_observacoes,
                                            "descricao": nova_descricao,
                                            "data_execucao_atividade": nova_data_execucao.strftime("%Y-%m-%d"),
                                            "data_retorno_atividade": nova_data_retorno.strftime("%Y-%m-%d") if nova_data_retorno else None,
                                        }}
                                    )
                                    st.success("Atividade atualizada com sucesso!")
                                    st.rerun()

                        if st.button("🗑️ Remover Atividade"):
                            collection_atividades.delete_one({"atividade_id": atividade_dados["atividade_id"]})
                            st.success("Atividade removida com sucesso!")
                            st.rerun()
