import streamlit as st
from utils.database import get_collection
from datetime import datetime, timedelta
import pandas as pd



def calcular_data_execucao(opcao):
    """Calcula a data de execução da tarefa com base na opção selecionada"""
    hoje = datetime.today().date()
    
    opcoes_prazo = {
        "Hoje": hoje,
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
                    prazo = st.selectbox("Prazo", ["Hoje", "1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"], index=3)

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
                                    ["Hoje", "1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"],
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



MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

@st.fragment
def gerenciamento_tarefas_por_usuario(user, admin):
    collection_tarefas = get_collection("tarefas")
    collection_atividades = get_collection("atividades")
    collection_empresas = get_collection("empresas")

    # 🔹 Filtra diretamente as tarefas do usuário logado
    cnpjs_usuario = {empresa["cnpj"] for empresa in collection_empresas.find({"usuario": user}, {"cnpj": 1})}
    
    if not cnpjs_usuario:
        st.warning("Nenhuma empresa atribuída a você.")
        return

    # 📅 Criar filtros de período
    hoje = datetime.today().date()
    amanha = hoje + timedelta(days=1)
    fim_semana = hoje + timedelta(days=7)
    fim_mes = hoje + timedelta(days=30)

    # 🔹 Filtragem no banco para otimizar carregamento
    tarefas = list(collection_tarefas.find(
        {"empresa": {"$in": list(cnpjs_usuario)}},
        {"_id": 0, "tarefa_id": 0, "atividade_vinculada": 0}
    ))

    if not tarefas:
        st.warning("Nenhuma tarefa encontrada.")
        return

    # 🔹 Criar um dicionário com Nome da Empresa baseado no CNPJ
    empresas_dict = {empresa["cnpj"]: empresa["razao_social"] for empresa in collection_empresas.find(
        {"cnpj": {"$in": list(cnpjs_usuario)}}, {"cnpj": 1, "razao_social": 1}
    )}

    # 🔹 Adicionar Nome da Empresa e converter datas
    for tarefa in tarefas:
        tarefa["Nome da Empresa"] = empresas_dict.get(tarefa["empresa"], "Não encontrado")
        tarefa["Data de Execução"] = pd.to_datetime(tarefa["data_execucao"]).date()

    # 📌 Criar abas para filtros rápidos
    abas = st.tabs([
        f"Hoje ({hoje.strftime('%d/%m')})",
        f"Amanhã ({amanha.strftime('%d/%m')})",
        f"Nesta semana (até {fim_semana.strftime('%d/%m')})",
        f"Neste mês (até {fim_mes.strftime('%d/%m')})"
    ])

    def filtrar_tarefas(data_inicio, data_fim):
        return [t for t in tarefas if data_inicio <= t["Data de Execução"] <= data_fim]

    tarefas_hoje = filtrar_tarefas(hoje, hoje)
    tarefas_amanha = filtrar_tarefas(amanha, amanha)
    tarefas_semana = filtrar_tarefas(hoje, fim_semana)
    tarefas_mes = filtrar_tarefas(hoje, fim_mes)

    # 📌 Criar abas para Hoje, Amanhã, Semana, Mês
    for aba, tarefas_periodo, titulo, data_limite in zip(
        abas,
        [tarefas_hoje, tarefas_amanha, tarefas_semana, tarefas_mes],
        ["Hoje", "Amanhã", "Nesta Semana", "Neste Mês"],
        [hoje, amanha, fim_semana, fim_mes]
    ):
        with aba:
            # Garantir que todas as datas estejam no formato correto antes da filtragem
            for t in tarefas_periodo:
                t["Data de Execução"] = pd.to_datetime(t["Data de Execução"], errors="coerce").date()

            # Contagem correta das tarefas atrasadas
            num_tarefas_atrasadas = sum(1 for t in tarefas_periodo if t["status"] == "🟥 Atrasado" and t["Data de Execução"] < hoje)
            st.write(1111)
            st.subheader(f"🟥 Atrasado - {titulo} ({num_tarefas_atrasadas})")

            # Filtrar tarefas atrasadas corretamente
            df_atrasadas = pd.DataFrame([t for t in tarefas_periodo if t["status"] == "🟥 Atrasado" and t["Data de Execução"] < hoje])

            if not df_atrasadas.empty:
                df_atrasadas = df_atrasadas.rename(columns={"titulo": "Título", "empresa": "CNPJ", "observacoes": "Observações"})
                df_atrasadas["Data de Execução"] = pd.to_datetime(df_atrasadas["Data de Execução"], errors="coerce").dt.strftime("%d/%m/%Y")
                df_atrasadas = df_atrasadas[["Data de Execução", "Nome da Empresa", "Título", "Observações"]]
                st.dataframe(df_atrasadas, hide_index=True, use_container_width=True)
            else:
                st.success(f"Nenhuma tarefa atrasada para {titulo}.")

            st.write('---')
            st.subheader(f"🟨 Em andamento - {titulo} ({len([t for t in tarefas_periodo if t['status'] == '🟨 Em andamento' and t['Data de Execução'] <= data_limite])})")
            
            df_em_andamento = pd.DataFrame([t for t in tarefas_periodo if t['status'] == '🟨 Em andamento' and t['Data de Execução'] <= data_limite])
            if not df_em_andamento.empty:
                df_em_andamento = df_em_andamento.rename(columns={"titulo": "Título", "empresa": "CNPJ", "observacoes": "Observações"})
                #df_em_andamento["Data de Execução"] = df_em_andamento["Data de Execução"].astype(str)
                df_em_andamento = df_em_andamento[["Data de Execução", "Nome da Empresa", "Título", "Observações"]]
                st.dataframe(df_em_andamento, hide_index=True, use_container_width=True)
            else:
                st.success(f"Nenhuma tarefa em andamento para {titulo}.")


def editar_tarefa_modal(tarefas, empresa_cnpj, key):
    """
    Exibe um pop-up/modal para edição de tarefas selecionadas.
    """
    collection_tarefas = get_collection("tarefas")
    collection_atividades = get_collection("atividades")
    collection_empresas = get_collection("empresas")

    with st.popover(f"✏️ Editar Tarefa"):
        tarefas_opcoes = {t["titulo"]: t for t in tarefas}
        tarefa_selecionada = st.selectbox(
            "Selecione uma tarefa para editar",
            options=list(tarefas_opcoes.keys()),
            key=f"select_editar_tarefa_{key}"  # 🔹 Chave única agora inclui `key`
        )

        if tarefa_selecionada:
            tarefa_dados = tarefas_opcoes[tarefa_selecionada]
            with st.form(f"form_editar_tarefa_{key}"):  # 🔹 Chave única no formulário
                st.subheader("✏️ Editar Tarefa")

                col1, col2 = st.columns(2)
                with col1:
                    titulo_edit = st.text_input("Título", value=tarefa_dados["titulo"], key=f"titulo_edit_{key}")
                    prazo_edit = st.selectbox(
                        "Novo Prazo de Execução",
                        ["Hoje", "1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"],
                        index=3,
                        key=f"prazo_edit_{key}"
                    )
                    data_execucao_edit = st.date_input(
                        "Data de Execução",
                        value=pd.to_datetime(tarefa_dados["Data de Execução"]).date(),
                        key=f"data_execucao_edit_{key}"
                    ) if prazo_edit == "Personalizada" else calcular_data_execucao(prazo_edit)

                with col2:
                    status_edit = st.selectbox(
                        "Status",
                        ["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"],
                        index=["🟥 Atrasado", "🟨 Em andamento", "🟩 Concluída"].index(tarefa_dados["status"]),
                        key=f"status_edit_{key}"
                    )
                    observacoes_edit = st.text_area("Observações", value=tarefa_dados["observacoes"], key=f"observacoes_edit_{key}")

                submit_editar = st.form_submit_button("💾 Salvar Alterações")

                if submit_editar:
                    tarefas_ativas = list(collection_tarefas.find({"empresa": empresa_cnpj, "status": {"$in": ["🟨 Em andamento", "🟥 Atrasado"]}}, {"_id": 0}))
                    if len(tarefas_ativas) == 1 and tarefa_dados["status"] in ["🟨 Em andamento", "🟥 Atrasado"] and status_edit == "🟩 Concluída":
                        st.error("⚠️ Pelo menos uma tarefa precisa estar 'Em andamento' ou 'Atrasada'.")
                    else:
                        if status_edit == "🟩 Concluída":
                            data_execucao_edit = datetime.today().date()
                            nova_atividade = {
                                "atividade_id": str(datetime.now().timestamp()),
                                "tipo_atividade": "Observação",
                                "status": "Registrado",
                                "titulo": f"Tarefa '{titulo_edit}' concluída",
                                "empresa": empresa_cnpj,
                                "descricao": f"O vendedor concluiu a tarefa '{titulo_edit}'.",
                                "data_execucao_atividade": datetime.today().strftime("%Y-%m-%d"),
                                "data_criacao_atividade": datetime.today().strftime("%Y-%m-%d")
                            }
                            collection_atividades.insert_one(nova_atividade)

                        resultado = collection_tarefas.update_one(
                            {"empresa": empresa_cnpj, "titulo": tarefa_dados["titulo"]},
                            {"$set": {
                                "titulo": titulo_edit,
                                "data_execucao": data_execucao_edit.strftime("%Y-%m-%d"),
                                "observacoes": observacoes_edit,
                                "status": status_edit
                            }}
                        )

                        # 🔹 Verifica se houve alguma alteração no banco
                        if resultado.modified_count > 0:
                            st.success("Tarefa atualizada com sucesso! 🔄")
                            st.rerun()  # Força a atualização da interface
                        else:
                            st.warning("Nenhuma alteração foi feita.")



