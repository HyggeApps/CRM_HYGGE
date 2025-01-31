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

            # Renomear colunas para exibição
            df_tarefas = df_tarefas.rename(
                columns={
                    "titulo": "Título",
                    "data_execucao": "Data de Execução",
                    "observacoes": "Observações",
                    "status": "Status"
                }
            )

            df_tarefas = df_tarefas[["Status", "Data de Execução", "Título", "Observações"]]

            # Converter datas para formato legível
            hoje = datetime.today().date()
            df_tarefas["Data Execução Timestamp"] = pd.to_datetime(df_tarefas["Data de Execução"], format="%d/%m/%Y", errors="coerce")

            # Atualizar status automaticamente antes de exibir a tabela
            df_tarefas["Status Corrigido"] = df_tarefas.apply(
                lambda row: "🟥 Atrasado" if row["Data Execução Timestamp"].date() < hoje and row["Status"] != "🟩 Concluída" else row["Status"], axis=1
            )

            # Criar tabela editável sem a coluna auxiliar
            edited_df = st.data_editor(
                df_tarefas.drop(columns=["Data Execução Timestamp"]),  # Esconder coluna auxiliar
                column_config={
                    "Status Corrigido": st.column_config.SelectboxColumn(
                        "Status",
                        options=["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"]
                    )
                },
                hide_index=True,
                use_container_width=True
            )

            # Verificar se houve mudanças antes de atualizar o banco de dados
            if not edited_df.equals(df_tarefas.drop(columns=["Data Execução Timestamp"])):
                collection_tarefas = get_collection("tarefas")
                updates = []

                for index, row in edited_df.iterrows():
                    if row["Status Corrigido"] != df_tarefas.loc[index, "Status"]:
                        updates.append(
                            {
                                "filtro": {"titulo": row["Título"], "data_execucao": row["Data de Execução"]},
                                "update": {"$set": {"status": row["Status Corrigido"]}}
                            }
                        )

                if updates:
                    for update in updates:
                        collection_tarefas.update_one(update["filtro"], update["update"])

                    st.success("Status atualizado com sucesso! 🔄")
                    st.experimental_rerun()


    else:
        st.warning("Nenhuma tarefa cadastrada para esta empresa.")