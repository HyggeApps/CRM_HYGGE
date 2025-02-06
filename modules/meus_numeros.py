import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_collection

import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_collection

def contar_tarefas_por_usuario(user):
    """Conta as tarefas concluídas do usuário e compara com a média de todos os vendedores."""

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

    # 🔹 Buscar todos os usuários únicos cadastrados nas empresas
    vendedores_unicos = collection_empresas.distinct("usuario")
    total_vendedores = len(vendedores_unicos)

    if total_vendedores == 0:
        st.warning("❌ Nenhum vendedor encontrado para cálculo de média.")
        return

    # 🔹 Criar dicionário para armazenar os resultados do usuário e da média geral
    resultados_usuario = {periodo: 0 for periodo in periodos}
    media_vendedores = {periodo: 0 for periodo in periodos}

    # 🔹 Contar tarefas concluídas do usuário e calcular média geral
    for periodo, data_limite in periodos.items():
        # 🟢 Contar tarefas concluídas do usuário
        tarefas_usuario = collection_tarefas.count_documents({
            "empresa": {"$in": cnpjs_usuario},
            "status": "🟩 Concluída",
            "data_execucao": {"$gte": data_limite.strftime("%Y-%m-%d")}
        })
        resultados_usuario[periodo] = tarefas_usuario

        # 🟡 Contar todas as tarefas concluídas no período e calcular a média
        total_tarefas_concluidas = collection_tarefas.count_documents({
            "status": "🟩 Concluída",
            "data_execucao": {"$gte": data_limite.strftime("%Y-%m-%d")}
        })

        media_vendedores[periodo] = round(total_tarefas_concluidas / total_vendedores, 2)  # Média por vendedor

    # 🔹 Exibir os resultados no Streamlit com Selectbox para escolha do período
    with st.expander("**📊 Comparação das minhas tarefas concluídas vs. Média dos vendedores HYGGE**",expanded=True):
        st.write('----')
        # Criar uma seleção para que o usuário escolha o período desejado
        periodo_selecionado = st.selectbox(
            "📆 Selecione o período para análise:",
            list(resultados_usuario.keys()),
            index=1  # Define "Última Semana" como padrão
        )
        st.write('----')
        # Recuperar os valores do período selecionado
        qtd = resultados_usuario[periodo_selecionado]
        media_geral = media_vendedores[periodo_selecionado]
        diferenca = qtd - media_geral
        emoji = "🟢 Acima da média" if diferenca > 0 else "🟡 Na média" if diferenca == 0 else "🔴 Abaixo da média"
        # Exibir os resultados com base no período escolhido
        st.subheader(f"📆 {periodo_selecionado}")
        st.write(f"✅ **Suas tarefas concluídas:** {qtd}")
        st.write(f"📊 **Média geral dos vendedores:** {media_geral}")
        st.write(f"📌 **Desempenho:** {emoji}")
        st.write("---")

    return resultados_usuario, media_vendedores


def contar_atividades_por_usuario(user):
    """Conta as atividades registradas do usuário e compara com a média de todos os vendedores.
       Também exibe o tipo de atividade mais frequente."""
    
    # 🔹 Conectar às coleções do banco de dados
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

    # 🔹 Criar dicionário para armazenar os resultados do usuário e da média geral
    resultados_usuario = {periodo: 0 for periodo in periodos}
    media_vendedores = {periodo: 0 for periodo in periodos}
    tipos_atividade_usuario = {periodo: {} for periodo in periodos}
    tipos_atividade_geral = {periodo: {} for periodo in periodos}

    # 🔹 Contar atividades do usuário e calcular média geral
    for periodo, data_limite in periodos.items():
        # 🟢 Contar atividades do usuário
        atividades_usuario = list(collection_atividades.find({
            "empresa": {"$in": cnpjs_usuario},
            "data_execucao_atividade": {"$gte": data_limite.strftime("%Y-%m-%d")}
        }))

        resultados_usuario[periodo] = len(atividades_usuario)

        # 🟡 Contar todas as atividades registradas no período e calcular a média
        todas_atividades = list(collection_atividades.find({
            "data_execucao_atividade": {"$gte": data_limite.strftime("%Y-%m-%d")}
        }))

        media_vendedores[periodo] = round(len(todas_atividades) / total_vendedores, 2)  # Média por vendedor

        # 📌 Identificar o tipo de atividade mais frequente do usuário e no geral
        for atividade in atividades_usuario:
            tipo = atividade["tipo_atividade"]
            tipos_atividade_usuario[periodo][tipo] = tipos_atividade_usuario[periodo].get(tipo, 0) + 1

        for atividade in todas_atividades:
            tipo = atividade["tipo_atividade"]
            tipos_atividade_geral[periodo][tipo] = tipos_atividade_geral[periodo].get(tipo, 0) + 1

    # 🔹 Exibir os resultados no Streamlit com Selectbox para escolha do período
    with st.expander("**📊 Comparação das minhas atividades registradas vs. Média dos vendedores HYGGE**", expanded=True):
        st.write('----')
        # Criar uma seleção para que o usuário escolha o período desejado
        periodo_selecionado = st.selectbox(
            "📆 Selecione o período para análise:",
            list(resultados_usuario.keys()),
            index=1,  # Define "Última Semana" como padrão
            key=f"select_periodo_atividade_{user}"  # Adicionando uma chave única
        )
        st.write('----')
        # Recuperar os valores do período selecionado
        qtd = resultados_usuario[periodo_selecionado]
        media_geral = media_vendedores[periodo_selecionado]
        diferenca = qtd - media_geral
        emoji = "🟢 Acima da média" if diferenca > 0 else "🟡 Na média" if diferenca == 0 else "🔴 Abaixo da média"

        # Exibir os resultados com base no período escolhido
        st.subheader(f"📆 {periodo_selecionado}")
        st.write(f"✅ **Suas atividades registradas:** {qtd}")
        st.write(f"📊 **Média geral dos vendedores:** {media_geral}")
        st.write(f"📌 **Desempenho:** {emoji}")
        st.write("---")

        # 📊 Tipo de atividade mais frequente
        tipo_usuario = max(tipos_atividade_usuario[periodo_selecionado], key=tipos_atividade_usuario[periodo_selecionado].get, default="Nenhum")
        tipo_geral = max(tipos_atividade_geral[periodo_selecionado], key=tipos_atividade_geral[periodo_selecionado].get, default="Nenhum")

        st.subheader("📊 Tipo de atividade mais frequente")
        st.write(f"🔹 **Mais registrada por você:** {tipo_usuario}")
        st.write(f"🔹 **Mais registrada no geral:** {tipo_geral}")
        st.write("---")

