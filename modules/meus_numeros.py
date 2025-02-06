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
    empresas_usuario = list(collection_empresas.find({"usuario": user}, {"cnpj": 1}))
    cnpjs_usuario = [empresa["cnpj"] for empresa in empresas_usuario]

    if not cnpjs_usuario:
        st.warning(f"❌ Nenhuma empresa encontrada para o usuário {user}.")
        return

    # 🔹 Buscar todos os usuários únicos cadastrados nas empresas
    vendedores_unicos = collection_empresas.distinct("usuario")
    total_vendedores = len(vendedores_unicos)

    if total_vendedores == 0:
        st.warning("❌ Nenhum vendedor encontrado para cálculo de média.")
        return

    # 🔹 Criar dicionários para armazenar os resultados do usuário e da média geral
    resultados_usuario = {periodo: {"Tarefas": 0, "Atividades": 0} for periodo in periodos}
    media_vendedores = {periodo: {"Tarefas": 0, "Atividades": 0} for periodo in periodos}
    tipos_atividade_usuario = {periodo: {} for periodo in periodos}
    tipos_atividade_geral = {periodo: {} for periodo in periodos}

    # 🔹 Contar tarefas e atividades do usuário e calcular médias gerais
    for periodo, data_limite in periodos.items():
        # 🟢 Contar tarefas concluídas do usuário
        tarefas_usuario = collection_tarefas.count_documents({
            "empresa": {"$in": cnpjs_usuario},
            "status": "🟩 Concluída",
            "data_execucao": {"$gte": data_limite.strftime("%Y-%m-%d")}
        })
        resultados_usuario[periodo]["Tarefas"] = tarefas_usuario

        # 🟢 Contar atividades registradas do usuário
        atividades_usuario = list(collection_atividades.find({
            "empresa": {"$in": cnpjs_usuario},
            "data_execucao_atividade": {"$gte": data_limite.strftime("%Y-%m-%d")}
        }))
        resultados_usuario[periodo]["Atividades"] = len(atividades_usuario)

        # 🟡 Contar todas as tarefas concluídas no período e calcular a média
        total_tarefas_concluidas = collection_tarefas.count_documents({
            "status": "🟩 Concluída",
            "data_execucao": {"$gte": data_limite.strftime("%Y-%m-%d")}
        })
        media_vendedores[periodo]["Tarefas"] = round(total_tarefas_concluidas / total_vendedores, 2)

        # 🟡 Contar todas as atividades registradas no período e calcular a média
        todas_atividades = list(collection_atividades.find({
            "data_execucao_atividade": {"$gte": data_limite.strftime("%Y-%m-%d")}
        }))
        media_vendedores[periodo]["Atividades"] = round(len(todas_atividades) / total_vendedores, 2)

        # 📌 Identificar o tipo de atividade mais frequente do usuário e no geral
        for atividade in atividades_usuario:
            tipo = atividade["tipo_atividade"]
            tipos_atividade_usuario[periodo][tipo] = tipos_atividade_usuario[periodo].get(tipo, 0) + 1

        for atividade in todas_atividades:
            tipo = atividade["tipo_atividade"]
            tipos_atividade_geral[periodo][tipo] = tipos_atividade_geral[periodo].get(tipo, 0) + 1

    # 🔹 Exibir os resultados no Streamlit quando o botão for pressionado
    if st.button("🚀 Compilar meus números"):
        with st.expander("📊 **Comparação do meu desempenho vs. Média dos vendedores**", expanded=True):
            st.write("----")

            # Criar um selectbox para escolha do período
            periodo_selecionado = st.selectbox(
                "📆 Selecione o período para análise:",
                list(resultados_usuario.keys()),
                index=1,  # Define "Última Semana" como padrão
                key=f"select_periodo_geral_{user}"
            )
            st.write("----")

            # Recuperar os valores do período selecionado
            qtd_tarefas = resultados_usuario[periodo_selecionado]["Tarefas"]
            media_tarefas = media_vendedores[periodo_selecionado]["Tarefas"]
            diferenca_tarefas = qtd_tarefas - media_tarefas
            emoji_tarefas = "🟢 Acima da média" if diferenca_tarefas > 0 else "🟡 Na média" if diferenca_tarefas == 0 else "🔴 Abaixo da média"

            qtd_atividades = resultados_usuario[periodo_selecionado]["Atividades"]
            media_atividades = media_vendedores[periodo_selecionado]["Atividades"]
            diferenca_atividades = qtd_atividades - media_atividades
            emoji_atividades = "🟢 Acima da média" if diferenca_atividades > 0 else "🟡 Na média" if diferenca_atividades == 0 else "🔴 Abaixo da média"

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
            tarefas_detalhadas = list(collection_tarefas.find({
                "empresa": {"$in": cnpjs_usuario},
                "status": "🟩 Concluída",
                "data_execucao": {"$gte": data_inicio.strftime("%Y-%m-%d")}
            }, {"_id": 0, "data_execucao": 1}))

            # Criar um dicionário para armazenar as contagens diárias
            contagem_diaria = {data_inicio + timedelta(days=i): 0 for i in range((hoje - data_inicio).days + 1)}

            # Preencher os dados do gráfico
            for tarefa in tarefas_detalhadas:
                data_tarefa = datetime.strptime(tarefa["data_execucao"], "%Y-%m-%d").date()
                if data_tarefa in contagem_diaria:
                    contagem_diaria[data_tarefa] += 1

            # Converter para DataFrame e exibir gráfico
            df_tarefas = pd.DataFrame(list(contagem_diaria.items()), columns=["Data", "Tarefas Concluídas"])
            df_tarefas = df_tarefas.sort_values(by="Data")
            st.subheader(f"📈 Evolução das Tarefas Concluídas ({periodo_selecionado})")
            st.line_chart(df_tarefas.set_index("Data"))


