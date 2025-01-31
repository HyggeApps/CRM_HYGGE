import streamlit as st
from utils.database import get_collection
from datetime import datetime, timedelta
import pandas as pd

def calcular_data_execucao(opcao):
    """Calcula a data de execução da tarefa com base na opção selecionada"""
    hoje = datetime.today().date()
    
    opcoes_prazo = {
        "1 dia útil": hoje + timedelta(days=1),
        "2 dias úteis": hoje + timedelta(days=2),
        "3 dias úteis": hoje + timedelta(days=3),
        "1 semana": hoje + timedelta(weeks=1),
        "2 semanas": hoje + timedelta(weeks=2),
        "1 mês": hoje + timedelta(days=30),
        "2 meses": hoje + timedelta(days=60),
        "3 meses": hoje + timedelta(days=90),
        "Personalizada": None  # Será definida manualmente
    }
    
    return opcoes_prazo.get(opcao, hoje)

def gerenciamento_tarefas(user, admin, empresa_cnpj):
    collection_tarefas = get_collection("tarefas")

    if not empresa_cnpj:
        st.error("Erro: Nenhuma empresa selecionada para gerenciar tarefas.")
        return

    # 📌 Botão para adicionar nova tarefa
    if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):
        with st.popover('➕ Criar Tarefa'):
            with st.form("form_criar_tarefa"):
                st.subheader("➕ Nova Tarefa")


                titulo = st.text_input("Título da Tarefa *")
                col1, col2 = st.columns(2)
                
                with col1:
                    prazo = st.selectbox("Prazo", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses", "Personalizada"], index=3)

                with col2:
                    data_execucao = st.date_input("Data de Execução", value=calcular_data_execucao(prazo)) if prazo == "Personalizada" else calcular_data_execucao(prazo)
                    status = st.selectbox("Status", ["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"], index=0)

                observacoes = st.text_area("Observações da Tarefa")

                submit_criar = st.form_submit_button("✅ Criar Tarefa")

        if submit_criar:
            if titulo:
                nova_tarefa = {
                    "titulo": titulo,
                    "empresa": empresa_cnpj,
                    "data_execucao": data_execucao.strftime("%Y-%m-%d"),
                    "observacoes": observacoes,
                    "status": status
                }
                collection_tarefas.insert_one(nova_tarefa)
                st.success("Tarefa criada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o campo obrigatório: Título da Tarefa.")


                if submit_criar:
                    if titulo:
                        nova_tarefa = {
                            "titulo": titulo,
                            "empresa": empresa_cnpj,
                            "data_execucao": data_execucao.strftime("%Y-%m-%d"),
                            "observacoes": observacoes,
                            "status": status
                        }
                        collection_tarefas.insert_one(nova_tarefa)
                        st.success("Tarefa criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha o campo obrigatório: Título da Tarefa.")

    # 📌 Listagem das tarefas existentes
    tarefas = list(collection_tarefas.find({"empresa": empresa_cnpj}, {"_id": 0}))

    if tarefas:
        with st.expander('📋 Tarefas Registradas', expanded=True):
            df_tarefas = pd.DataFrame(tarefas)

            df_tarefas = df_tarefas.rename(
                columns={
                    "titulo": "Título",
                    "data_execucao": "Data de Execução",
                    "observacoes": "Observações",
                    "status": "Status"
                }
            )

            df_tarefas = df_tarefas[["Status", "Data de Execução", "Título", "Observações", "Status"]]
            df_tarefas["Data de Execução"] = pd.to_datetime(df_tarefas["Data de Execução"], errors="coerce").dt.strftime("%d/%m/%Y")

            st.dataframe(df_tarefas, hide_index=True, use_container_width=True)

            # 📌 Popover para editar tarefas existentes
            with st.popover('✏️ Editar Tarefa'):
                tarefa_selecionada = st.selectbox(
                    "Selecione uma tarefa para editar",
                    options=[t["titulo"] for t in tarefas],
                    key="select_editar_tarefa"
                )

                if tarefa_selecionada:
                    tarefa_dados = collection_tarefas.find_one({"empresa": empresa_cnpj, "titulo": tarefa_selecionada}, {"_id": 0})

                    if tarefa_dados:
                        with st.form("form_editar_tarefa"):
                            st.subheader("✏️ Editar Tarefa")

                            titulo_edit = st.text_input("Título", value=tarefa_dados["titulo"])
                            prazo_edit = st.selectbox("Novo Prazo de Execução", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses", "Personalizada"], index=3)
                            
                            data_execucao_edit = st.date_input("Data de Execução", value=pd.to_datetime(tarefa_dados["data_execucao"]).date()) if prazo_edit == "Personalizada" else calcular_data_execucao(prazo_edit)
                            
                            observacoes_edit = st.text_area("Observações", value=tarefa_dados["observacoes"])
                            status_edit = st.selectbox("Status", ["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"], index=["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"].index(tarefa_dados["status"]))

                            submit_editar = st.form_submit_button("💾 Salvar Alterações")

                            if submit_editar:
                                collection_tarefas.update_one(
                                    {"empresa": empresa_cnpj, "titulo": tarefa_selecionada},
                                    {"$set": {
                                        "titulo": titulo_edit,
                                        "data_execucao": data_execucao_edit.strftime("%Y-%m-%d"),
                                        "observacoes": observacoes_edit,
                                        "status": status_edit
                                    }}
                                )
                                st.success("Tarefa atualizada com sucesso!")
                                st.rerun()
    else:
        st.warning("Nenhuma tarefa cadastrada para esta empresa.")