import streamlit as st
from utils.database import get_collection
from datetime import datetime, timedelta
import pandas as pd
import time

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
        "3 meses": hoje + timedelta(days=90)
    }
    
    return opcoes_prazo.get(opcao, hoje)

@st.fragment
def atualizar_status_tarefas(empresa_cnpj):
    collection_tarefas = get_collection("tarefas")
    # 📌 Verificar e atualizar tarefas atrasadas automaticamente
    tarefas = list(collection_tarefas.find({"empresa": empresa_cnpj}, {"_id": 0}))
    hoje = datetime.today().date()
    atualizacoes_realizadas = False

    for tarefa in tarefas:
        data_execucao = datetime.strptime(tarefa["data_execucao"], "%Y-%m-%d").date()
        
        if data_execucao < hoje and tarefa["status"] != "🟩 Concluída":
            collection_tarefas.update_one(
                {"empresa": empresa_cnpj, "titulo": tarefa["titulo"]},
                {"$set": {"status": "🟥 Atrasado"}}
            )
    
    collection_tarefas = get_collection("tarefas")
    return collection_tarefas

@st.fragment
def gerenciamento_tarefas(user, admin, empresa_cnpj):
    collection_tarefas = atualizar_status_tarefas(empresa_cnpj)
    collection_atividades = get_collection("atividades")

    if not empresa_cnpj:
        st.error("Erro: Nenhuma empresa selecionada para gerenciar tarefas.")
        return

    # 📌 Verificar e atualizar tarefas atrasadas automaticamente
    tarefas = list(collection_tarefas.find({"empresa": empresa_cnpj}, {"_id": 0}))
    hoje = datetime.today().date()

    for tarefa in tarefas:
        data_execucao = datetime.strptime(tarefa["data_execucao"], "%Y-%m-%d").date()
        
        if data_execucao < hoje and tarefa["status"] != "🟩 Concluída":
            collection_tarefas.update_one(
                {"empresa": empresa_cnpj, "titulo": tarefa["titulo"]},
                {"$set": {"status": "🟥 Atrasado"}}
            )


    # 📌 Botão para adicionar nova tarefa
    if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):
        with st.popover('➕ Criar Tarefa'):
            with st.form("form_criar_tarefa"):
                st.subheader("➕ Nova Tarefa")

                titulo = st.text_input("Título da Tarefa *")
                col1, col2 = st.columns(2)
                
                with col1:
                    prazo = st.selectbox("Prazo", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"], index=3)

                with col2:
                    data_execucao = st.date_input("Data de Execução", value=calcular_data_execucao(prazo)) if prazo == "Personalizada" else calcular_data_execucao(prazo)
                    hoje = datetime.today().date()
                    status = st.selectbox("Status", ["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"], index=1)
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
                    
                    # 🔄 Atualizar a última atividade da empresa
                    data_hoje = datetime.now().strftime("%Y-%m-%d")  # Data atual
                    collection_empresas = get_collection("empresas")
                    collection_empresas.update_one(
                        {"cnpj": empresa_cnpj},
                        {"$set": {"ultima_atividade": data_hoje}}
                    )

                    st.success("Tarefa criada com sucesso!")
                    st.rerun()
                    
                    
                else:
                    st.error("Preencha o campo obrigatório: Título da Tarefa.")

    # 📌 Listagem das tarefas existentes
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

            df_tarefas = df_tarefas[["Status", "Data de Execução", "Título", "Observações"]]
            df_tarefas["Data de Execução"] = pd.to_datetime(df_tarefas["Data de Execução"], errors="coerce").dt.strftime("%d/%m/%Y")

            st.dataframe(df_tarefas, hide_index=True, use_container_width=True)

            # 📌 Popover para editar tarefas existentes
            with st.popover('✏️ Editar Tarefa'):
                # Filtrar apenas as tarefas que não estão concluídas
                tarefas_nao_concluidas = [t for t in tarefas if t["status"] != "🟩 Concluída"]

                tarefa_selecionada = st.selectbox(
                    "Selecione uma tarefa para editar",
                    options=[t["titulo"] for t in tarefas_nao_concluidas],  # Apenas tarefas em andamento ou atrasadas
                    key="select_editar_tarefa"
                )

                if tarefa_selecionada:
                    tarefa_dados = collection_tarefas.find_one({"empresa": empresa_cnpj, "titulo": tarefa_selecionada}, {"_id": 0})
                    if tarefa_dados:
                        with st.form("form_editar_tarefa",):
                            st.subheader("✏️ Editar Tarefa")

                            # Criar duas colunas para organizar os campos
                            col1, col2 = st.columns(2)

                            with col1:
                                titulo_edit = st.text_input("Título", value=tarefa_dados["titulo"])
                                prazo_edit = st.selectbox(
                                    "Novo Prazo de Execução",
                                    ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"],
                                    index=3
                                )
                                data_execucao_edit = st.date_input(
                                    "Data de Execução",
                                    value=pd.to_datetime(tarefa_dados["data_execucao"]).date()
                                ) if prazo_edit == "Personalizada" else calcular_data_execucao(prazo_edit)

                            with col2:
                                status_edit = st.selectbox(
                                    "Status",
                                    ["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"],
                                    index=["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"].index(tarefa_dados["status"])
                                )
                                observacoes_edit = st.text_area("Observações", value=tarefa_dados["observacoes"])

                            # Botão para salvar as alterações
                            submit_editar = st.form_submit_button("💾 Salvar Alterações")

                            if submit_editar:
                                # Verificar se o usuário está tentando concluir todas as tarefas
                                tarefas_ativas = list(collection_tarefas.find({"empresa": empresa_cnpj, "status": {"$in": ["🟨 Em andamento", "🟥 Atrasado"]}}, {"_id": 0}))

                                if len(tarefas_ativas) == 1 and tarefa_dados["status"] in ["🟨 Em andamento", "🟥 Atrasado"] and status_edit == "🟩 Concluída":
                                    st.error("⚠️ Erro: Pelo menos uma tarefa precisa estar 'Em andamento' ou 'Atrasada'. Cadastre uma nova atividade/tarefa antes de concluir todas.")
                                else:
                                    if status_edit == "🟩 Concluída":
                                        data_execucao_edit = datetime.today().date()

                                        # Criar uma nova atividade informando que a tarefa foi concluída
                                        nova_atividade = {
                                            "atividade_id": str(datetime.now().timestamp()),  
                                            "tipo_atividade": "Observação",
                                            "status": "Registrado",
                                            "titulo": f"Tarefa '{titulo_edit}' concluída",
                                            "empresa": empresa_cnpj,
                                            "descricao": f"O vendedor {user} concluiu a tarefa '{titulo_edit}'.",
                                            "data_execucao_atividade": datetime.today().strftime("%Y-%m-%d"),
                                            "data_criacao_atividade": datetime.today().strftime("%Y-%m-%d")
                                        }

                                        # Inserir no banco de atividades
                                        collection_atividades.insert_one(nova_atividade)

                                    # Atualizar a tarefa no banco
                                    collection_tarefas.update_one(
                                        {"empresa": empresa_cnpj, "titulo": tarefa_selecionada},
                                        {"$set": {
                                            "titulo": titulo_edit,
                                            "data_execucao": data_execucao_edit.strftime("%Y-%m-%d"),
                                            "observacoes": observacoes_edit,
                                            "status": status_edit
                                        }}
                                    )
                                    
                                    # 🔄 Atualizar a última atividade da empresa
                                    data_hoje = datetime.now().strftime("%Y-%m-%d")  # Data atual
                                    collection_empresas = get_collection("empresas")
                                    collection_empresas.update_one(
                                        {"cnpj": empresa_cnpj},
                                        {"$set": {"ultima_atividade": data_hoje}}
                                    )
                                    st.success("Tarefa atualizada com sucesso! 🔄")
                                    st.rerun()
                                    
                                    

    else:
        st.warning("Nenhuma tarefa cadastrada para esta empresa.")


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from utils.database import get_collection

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from utils.database import get_collection

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

@st.fragment
def visualizar_tarefas_por_usuario(user, admin):
    collection_tarefas = get_collection("tarefas")
    collection_empresas = get_collection("empresas")

    st.subheader("📋 Minhas Tarefas")

    # Para admin, permitir selecionar qualquer usuário. Para vendedor, apenas suas tarefas
    if admin:
        usuarios = list(collection_empresas.distinct("usuario"))
        usuario_selecionado = st.selectbox("Filtrar por usuário", ["Todos"] + usuarios, index=0)
    else:
        usuario_selecionado = user  # Vendedor só vê suas próprias tarefas

    # Construir query para buscar tarefas
    query = {}
    if usuario_selecionado != "Todos":
        query["empresa"] = {"$in": [empresa["cnpj"] for empresa in collection_empresas.find({"usuario": usuario_selecionado}, {"cnpj": 1})]}

    # Buscar tarefas filtradas
    tarefas = list(collection_tarefas.find(query, {"_id": 0, "tarefa_id": 0, "atividade_vinculada": 0}))

    if not tarefas:
        st.warning("Nenhuma tarefa encontrada.")
        return

    # Criar um dicionário com Nome da Empresa baseado no CNPJ
    empresas_dict = {empresa["cnpj"]: empresa["razao_social"] for empresa in collection_empresas.find({}, {"cnpj": 1, "razao_social": 1})}

    # Adicionar o Nome da Empresa e converter data
    for tarefa in tarefas:
        tarefa["Nome da Empresa"] = empresas_dict.get(tarefa["empresa"], "Não encontrado")
        tarefa["Data de Execução"] = pd.to_datetime(tarefa["data_execucao"])

    # 📅 Criar filtros de período
    hoje = datetime.today().date()
    amanha = hoje + timedelta(days=1)
    fim_semana = hoje + timedelta(days=7)
    fim_mes = hoje + timedelta(days=30)
    ano_atual = hoje.year
    mes_atual = hoje.month

    # Opções de Filtro
    meses_opcoes = [f"{MESES_PT[m]} {ano_atual}" for m in range(1, 13)]
    trimestres_opcoes = [f"Trimestre {i} ({MESES_PT[i*3-2]} - {MESES_PT[i*3]}) {ano_atual}" for i in range(1, 5)]
    semestres_opcoes = [f"Semestre {i} ({MESES_PT[i*6-5]} - {MESES_PT[i*6]}) {ano_atual}" for i in range(1, 3)]
    anos_opcoes = [str(y) for y in range(ano_atual - 4, ano_atual + 1)]

    # Seleção de período
    filtro_tipo = st.radio("📅 Filtrar por:", ["Mês", "Trimestre", "Semestre", "Ano"], horizontal=True)
    if filtro_tipo == "Mês":
        periodo_selecionado = st.selectbox("Escolha o mês", meses_opcoes, index=mes_atual - 1)
        mes_inicio = int(periodo_selecionado.split()[1])
        tarefas_periodo = [t for t in tarefas if t["Data de Execução"].month == mes_inicio and t["Data de Execução"].year == ano_atual]

    elif filtro_tipo == "Trimestre":
        periodo_selecionado = st.selectbox("Escolha o trimestre", trimestres_opcoes)
        trimestre = int(periodo_selecionado.split()[1])
        meses_trimestre = list(range((trimestre - 1) * 3 + 1, trimestre * 3 + 1))
        tarefas_periodo = [t for t in tarefas if t["Data de Execução"].month in meses_trimestre and t["Data de Execução"].year == ano_atual]

    elif filtro_tipo == "Semestre":
        periodo_selecionado = st.selectbox("Escolha o semestre", semestres_opcoes)
        semestre = int(periodo_selecionado.split()[1])
        meses_semestre = list(range((semestre - 1) * 6 + 1, semestre * 6 + 1))
        tarefas_periodo = [t for t in tarefas if t["Data de Execução"].month in meses_semestre and t["Data de Execução"].year == ano_atual]

    else:  # Ano
        periodo_selecionado = st.selectbox("Escolha o ano", anos_opcoes, index=4)
        ano_escolhido = int(periodo_selecionado)
        tarefas_periodo = [t for t in tarefas if t["Data de Execução"].year == ano_escolhido]

    # Contagem de status para gráficos
    total_finalizadas = sum(1 for t in tarefas_periodo if t["status"] == "🟩 Concluída")
    total_andamento = sum(1 for t in tarefas_periodo if t["status"] == "🟨 Em andamento")
    total_atrasadas = sum(1 for t in tarefas_periodo if t["status"] == "🟥 Atrasado")

    st.subheader("📊 Resumo das Tarefas")

    col1, col2 = st.columns([2, 3])  # Ajuste de tamanho das colunas

    with col1:
        # Criar gráfico de pizza menor e com fundo transparente
        fig, ax = plt.subplots(figsize=(3, 3))
        labels = ["Finalizadas", "Em andamento", "Atrasadas"]
        valores = [total_finalizadas, total_andamento, total_atrasadas]
        cores = ["#2ECC71", "#F1C40F", "#E74C3C"]

        ax.pie(valores, labels=labels, autopct="%1.1f%%", colors=cores, startangle=90)
        ax.axis("equal")  # Mantém formato circular
        fig.patch.set_alpha(0)  # Fundo transparente
        st.pyplot(fig)

    with col2:
        # Exibir contagem total
        col1, col2, col3 = st.columns(3)
        col1.metric("🟩 Finalizadas", total_finalizadas)
        col2.metric("🟨 Em andamento", total_andamento)
        col3.metric("🟥 Atrasadas", total_atrasadas)

    if admin and usuario_selecionado == "Todos":
        st.subheader("📊 Comparativo por Usuário")

        # Contar tarefas por usuário
        df_tarefas = pd.DataFrame(tarefas_periodo)
        tarefas_por_usuario = df_tarefas.groupby(["empresa", "status"]).size().unstack(fill_value=0)

        # Criar gráfico de barras comparativo
        fig, ax = plt.subplots(figsize=(6, 3))
        tarefas_por_usuario.plot(kind="bar", stacked=True, color=["#2ECC71", "#F1C40F", "#E74C3C"], ax=ax)
        ax.set_xlabel("Usuário")
        ax.set_ylabel("Quantidade de Tarefas")
        ax.set_title("Comparativo de Tarefas por Usuário")
        st.pyplot(fig)


