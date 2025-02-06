import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_collection

def contar_atividades_tarefas(user):
    """Conta quantas atividades e tarefas o usuário fez nos últimos períodos definidos."""
    
    collection_atividades = get_collection("atividades")
    collection_tarefas = get_collection("tarefas")

    # 🔹 Definir períodos para análise
    hoje = datetime.today().date()
    periodos = {
        "Último Dia": hoje - timedelta(days=1),
        "Última Semana": hoje - timedelta(weeks=1),
        "Último Mês": hoje - timedelta(days=30),
        "Último Trimestre": hoje - timedelta(days=90),
        "Último Semestre": hoje - timedelta(days=180),
        "Último Ano": hoje - timedelta(days=365)
    }

    # 🔹 Criar dicionário para armazenar os resultados
    resultados = {periodo: {"Atividades": 0, "Tarefas": 0} for periodo in periodos}

    # 🔹 Contar atividades concluídas nos períodos
    for periodo, data_limite in periodos.items():
        atividades = collection_atividades.count_documents({
            "descricao": {"$regex": f".*{user}.*"},  # Busca atividades vinculadas ao usuário
            "data_execucao_atividade": {"$gte": data_limite.strftime("%Y-%m-%d")}
        })

        tarefas = collection_tarefas.count_documents({
            "status": "🟩 Concluída",  # Considerando apenas as tarefas concluídas
            "data_execucao": {"$gte": data_limite.strftime("%Y-%m-%d")}
        })

        # Armazenar resultados
        resultados[periodo]["Atividades"] = atividades
        resultados[periodo]["Tarefas"] = tarefas
    
    st.write(resultados)
    return resultados
