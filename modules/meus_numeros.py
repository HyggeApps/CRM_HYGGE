import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_collection

def compilar_meus_numeros(user):
    """Compila números de tarefas concluídas e atividades registradas do usuário e compara com a média dos vendedores."""

    # 🔹 Conectar às coleções do banco de dados
    collection_tarefas = get_collection("tarefas")
    collection_atividades = get_collection("atividades")
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
    empresas_usuario = collection_empresas.find({"usuario": user}, {"cnpj": 1})
    cnpjs_usuario = {empresa["cnpj"] for empresa in empresas_usuario}

    if not cnpjs_usuario:
        st.warning(f"❌ Nenhuma empresa encontrada para o usuário {user}.")
        return

    # 🔹 Buscar todos os usuários únicos cadastrados nas empresas
    vendedores_unicos = collection_empresas.distinct("usuario")
    total_vendedores = len(vendedores_unicos) if vendedores_unicos else 1

    # 🔹 Buscar todas as tarefas e atividades dentro do maior período necessário
    data_inicio_global = min(periodos.values())
    
    tarefas = list(collection_tarefas.find(
        {"data_execucao": {"$gte": data_inicio_global.strftime("%Y-%m-%d")}},
        {"empresa": 1, "status": 1, "data_execucao": 1}
    ))

    atividades = list(collection_atividades.find(
        {"data_execucao_atividade": {"$gte": data_inicio_global.strftime("%Y-%m-%d")}},
        {"empresa": 1, "tipo_atividade": 1, "data_execucao_atividade": 1}
    ))

    # 🔹 Criar dicionários para armazenar os resultados do usuário e da média geral
    resultados_usuario = {p: {"Tarefas": 0, "Atividades": 0} for p in periodos}
    media_vendedores = {p: {"Tarefas": 0, "Atividades": 0} for p in periodos}
    tipos_atividade_usuario = {p: {} for p in periodos}
    tipos_atividade_geral = {p: {} for p in periodos}

    # 🔹 Processar tarefas e atividades em memória
    for periodo, data_limite in periodos.items():
        # Filtrar tarefas e atividades dentro do período
        tarefas_periodo = [t for t in tarefas if t["data_execucao"] >= data_limite.strftime("%Y-%m-%d")]
        atividades_periodo = [a for a in atividades if a["data_execucao_atividade"] >= data_limite.strftime("%Y-%m-%d")]

        # 🟢 Contar tarefas concluídas do usuário
        resultados_usuario[periodo]["Tarefas"] = sum(1 for t in tarefas_periodo if t["empresa"] in cnpjs_usuario and t["status"] == "🟩 Concluída")

        # 🟡 Calcular a média de tarefas por vendedor
        total_tarefas_concluidas = sum(1 for t in tarefas_periodo if t["status"] == "🟩 Concluída")
        media_vendedores[periodo]["Tarefas"] = round(total_tarefas_concluidas / total_vendedores, 2)

        # 🟢 Contar atividades registradas do usuário
        resultados_usuario[periodo]["Atividades"] = sum(1 for a in atividades_periodo if a["empresa"] in cnpjs_usuario)

        # 🟡 Calcular a média de atividades por vendedor
        media_vendedores[periodo]["Atividades"] = round(len(atividades_periodo) / total_vendedores, 2)

        # 📌 Identificar o tipo de atividade mais frequente
        for atividade in atividades_periodo:
            tipo = atividade["tipo_atividade"]
            if atividade["empresa"] in cnpjs_usuario:
                tipos_atividade_usuario[periodo][tipo] = tipos_atividade_usuario[periodo].get(tipo, 0) + 1
            tipos_atividade_geral[periodo][tipo] = tipos_atividade_geral[periodo].get(tipo, 0) + 1

    with st.expander("📊 **Comparação do meu desempenho vs. Média dos vendedores**", expanded=True):
        st.write("----")

        # Criar um selectbox para escolha do período
        periodo_selecionado = st.selectbox(
            "📆 Selecione o período para análise:",
            list(resultados_usuario.keys()),
            index=1,
            key=f"select_periodo_geral_{user}"
        )
        st.write("----")

        # Recuperar os valores do período selecionado
        qtd_tarefas = resultados_usuario[periodo_selecionado]["Tarefas"]
        media_tarefas = media_vendedores[periodo_selecionado]["Tarefas"]
        emoji_tarefas = "🟢 Acima da média" if qtd_tarefas > media_tarefas else "🔴 Abaixo da média"

        qtd_atividades = resultados_usuario[periodo_selecionado]["Atividades"]
        media_atividades = media_vendedores[periodo_selecionado]["Atividades"]
        emoji_atividades = "🟢 Acima da média" if qtd_atividades > media_atividades else "🔴 Abaixo da média"

        # Exibir tarefas e atividades
        st.subheader(f"📆 {periodo_selecionado}")
        st.write(f"✅ **Suas tarefas concluídas:** {qtd_tarefas} ({emoji_tarefas})")
        st.write(f"📊 **Média geral de tarefas:** {media_tarefas}")
        st.write("---")
        st.write(f"✅ **Suas atividades registradas:** {qtd_atividades} ({emoji_atividades})")
        st.write(f"📊 **Média geral de atividades:** {media_atividades}")
        st.write("---")

        # 📊 Tipo de atividade mais frequente
        tipo_usuario = max(tipos_atividade_usuario[periodo_selecionado], key=tipos_atividade_usuario[periodo_selecionado].get, default="Nenhum")
        tipo_geral = max(tipos_atividade_geral[periodo_selecionado], key=tipos_atividade_geral[periodo_selecionado].get, default="Nenhum")

        st.subheader("📊 Tipo de atividade mais frequente")
        st.write(f"🔹 **Mais registrada por você:** {tipo_usuario}")
        st.write(f"🔹 **Mais registrada no geral:** {tipo_geral}")
        st.write("---")

        # 🔹 Criar um gráfico de linhas com base no período selecionado
        data_inicio = periodos[periodo_selecionado]
        df_tarefas = pd.DataFrame(
            [{"Data": datetime.strptime(t["data_execucao"], "%Y-%m-%d").date(), "Tarefas": 1} for t in tarefas if t["empresa"] in cnpjs_usuario and t["status"] == "🟩 Concluída" and t["data_execucao"] >= data_inicio.strftime("%Y-%m-%d")]
        )
        
        if not df_tarefas.empty:
            df_tarefas = df_tarefas.groupby("Data").sum().reset_index()
            st.subheader(f"📈 Evolução das Tarefas Concluídas ({periodo_selecionado})")
            st.line_chart(df_tarefas.set_index("Data"))
