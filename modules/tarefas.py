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


    tarefas = list(collection_tarefas.find({"empresa": empresa_cnpj}, {"_id": 0}))

    if tarefas:
        with st.expander('Tarefas registradas'):
            df_tarefas = pd.DataFrame(tarefas)

            df_tarefas = df_tarefas.rename(
                columns={
                    "titulo": "Título",
                    "data_execucao": "Data de Execução",
                    "observacoes": "Observações",
                    "status": 'Status'
                }
            )

            df_tarefas = df_tarefas[["Título", "Data de Execução", "Observações"]]
            df_tarefas["Data Execução"] = pd.to_datetime(df_tarefas["Data Execução"], errors="coerce").dt.strftime("%d/%m/%Y")

            st.dataframe(df_tarefas, hide_index=True, use_container_width=True)
    else:
        st.warning("Nenhuma tarefa cadastrada para esta empresa.")


