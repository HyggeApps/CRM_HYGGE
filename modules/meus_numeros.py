import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_collection

def contar_tarefas_por_usuario(user):
    """Conta quantas tarefas o usuário fez nos últimos períodos definidos, considerando as empresas vinculadas a ele."""

    # 🔹 Conectar às coleções do banco de dados
    collection_tarefas = get_collection("tarefas")
    collection_empresas = get_collection("empresas")

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

    # 🔹 Buscar os CNPJs das empresas associadas ao usuário
    empresas_usuario = list(collection_empresas.find({"usuario": user}, {"cnpj": 1}))
    cnpjs_usuario = [empresa["cnpj"] for empresa in empresas_usuario]

    if not cnpjs_usuario:
        st.warning(f"❌ Nenhuma empresa encontrada para o usuário {user}.")
        return

    # 🔹 Criar dicionário para armazenar os resultados
    resultados = {periodo: 0 for periodo in periodos}

    # 🔹 Contar tarefas concluídas nos períodos
    for periodo, data_limite in periodos.items():
        tarefas = collection_tarefas.count_documents({
            "empresa": {"$in": cnpjs_usuario},  # Filtra apenas tarefas das empresas do usuário
            "status": "🟩 Concluída",
            "data_execucao": {"$gte": data_limite.strftime("%Y-%m-%d")}
        })
        resultados[periodo] = tarefas

    # 🔹 Exibir os resultados
    st.write("### 📊 Relatório de Tarefas Concluídas do Usuário")
    for periodo, qtd in resultados.items():
        st.subheader(f"📆 {periodo}")
        st.write(f"✅ **Tarefas concluídas:** {qtd}")
        st.write("---")

    return resultados

