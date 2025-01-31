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

    st.info("Gerencie as tarefas vinculadas à empresa selecionada.")

    # Abas para gerenciamento de tarefas
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Tarefas da Empresa", "✏️ Editar Tarefa", "➕ Criar Tarefa", "🗑️ Remover Tarefa"])

    # 📋 Exibir Tarefas da Empresa
    with tab1:
        st.subheader("📋 Tarefas da Empresa")

        tarefas = list(collection_tarefas.find({"empresa": empresa_cnpj}, {"_id": 0}))

        if tarefas:
            df_tarefas = pd.DataFrame(tarefas)

            df_tarefas = df_tarefas.rename(
                columns={
                    "titulo": "Título",
                    "data_execucao": "Data Execução",
                    "observacoes": "Observações"
                }
            )

            df_tarefas = df_tarefas[["Título", "Data Execução", "Observações"]]
            df_tarefas["Data Execução"] = pd.to_datetime(df_tarefas["Data Execução"], errors="coerce").dt.strftime("%d/%m/%Y")

            st.dataframe(df_tarefas, hide_index=True, use_container_width=True)
        else:
            st.warning("Nenhuma tarefa cadastrada para esta empresa.")

    # ✏️ Editar Tarefa
    with tab2:
        st.subheader("✏️ Editar Tarefa")

        tarefas = list(collection_tarefas.find({"empresa": empresa_cnpj}, {"_id": 0, "titulo": 1}))

        if tarefas:
            tarefa_selecionada = st.selectbox(
                "Selecione uma tarefa para editar",
                options=[t["titulo"] for t in tarefas],
                key="select_editar_tarefa"
            )

            if tarefa_selecionada:
                tarefa_dados = collection_tarefas.find_one({"empresa": empresa_cnpj, "titulo": tarefa_selecionada}, {"_id": 0})

                if tarefa_dados:
                    with st.form("form_editar_tarefa", clear_on_submit=True):
                        st.subheader("✏️ Editar Tarefa")

                        titulo_edit = st.text_input("Título", value=tarefa_dados["titulo"])
                        prazo_edit = st.selectbox("Novo Prazo de Execução", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses", "Personalizada"], index=3)
                        
                        data_execucao_edit = st.date_input("Data de Execução", value=pd.to_datetime(tarefa_dados["data_execucao"]).date()) if prazo_edit == "Personalizada" else calcular_data_execucao(prazo_edit)
                        
                        observacoes_edit = st.text_area("Observações", value=tarefa_dados["observacoes"])

                        submit_editar = st.form_submit_button("💾 Salvar Alterações")

                        if submit_editar:
                            collection_tarefas.update_one(
                                {"empresa": empresa_cnpj, "titulo": tarefa_selecionada},
                                {"$set": {
                                    "titulo": titulo_edit,
                                    "data_execucao": data_execucao_edit.strftime("%Y-%m-%d"),
                                    "observacoes": observacoes_edit
                                }}
                            )
                            st.success("Tarefa atualizada com sucesso!")
                            st.rerun()

    # ➕ Criar Nova Tarefa
    with tab3:
        st.subheader("➕ Criar Nova Tarefa")

        with st.form("form_criar_tarefa", clear_on_submit=True):
            titulo = st.text_input("Título da Tarefa *")
            prazo = st.selectbox("Prazo de Execução", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses", "Personalizada"], index=3)
            
            data_execucao = st.date_input("Data de Execução", value=calcular_data_execucao(prazo)) if prazo == "Personalizada" else calcular_data_execucao(prazo)
            
            observacoes = st.text_area("Observações da Tarefa")

            submit_criar = st.form_submit_button("✅ Criar Tarefa")

            if submit_criar:
                if titulo:
                    nova_tarefa = {
                        "titulo": titulo,
                        "empresa": empresa_cnpj,
                        "data_execucao": data_execucao.strftime("%Y-%m-%d"),
                        "observacoes": observacoes
                    }
                    collection_tarefas.insert_one(nova_tarefa)
                    st.success("Tarefa criada com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha o campo obrigatório: Título da Tarefa.")

    # 🗑️ Remover Tarefa
    with tab4:
        st.subheader("🗑️ Remover Tarefa")

        tarefas = list(collection_tarefas.find({"empresa": empresa_cnpj}, {"_id": 0, "titulo": 1}))

        if tarefas:
            tarefa_selecionada = st.selectbox(
                "Selecione a tarefa para remover",
                options=[t["titulo"] for t in tarefas],
                key="select_remover_tarefa"
            )

            if st.button("❌ Remover Tarefa"):
                collection_tarefas.delete_one({"empresa": empresa_cnpj, "titulo": tarefa_selecionada})
                st.success(f"Tarefa '{tarefa_selecionada}' removida com sucesso!")
                st.rerun()
        else:
            st.warning("Nenhuma tarefa cadastrada para esta empresa.")
