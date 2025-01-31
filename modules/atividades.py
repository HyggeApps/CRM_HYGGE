from utils.database import get_collection
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import time

# Dicionário de meses em português
MESES_PT = {
    "January": "Janeiro", "February": "Fevereiro", "March": "Março",
    "April": "Abril", "May": "Maio", "June": "Junho",
    "July": "Julho", "August": "Agosto", "September": "Setembro",
    "October": "Outubro", "November": "Novembro", "December": "Dezembro"
}

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

@st.fragment
def exibir_atividades_empresa(user, admin, empresa_cnpj):
    collection_atividades = get_collection("atividades")
    collection_contatos = get_collection("contatos")

    if not empresa_cnpj:
        st.error("Erro: Nenhuma empresa selecionada para exibir atividades.")
        return

    # Buscar contatos vinculados à empresa
    contatos_vinculados = list(collection_contatos.find({"empresa": empresa_cnpj}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))

    # Criar lista de contatos formatada
    lista_contatos = [""] + [f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos_vinculados]

    # Buscar atividades vinculadas **somente** à empresa selecionada
    atividades = list(collection_atividades.find({"empresa": empresa_cnpj}, {"_id": 0}))

    # Dicionário de meses com valores numéricos para ordenação
    MESES_NUMERICOS = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3,
        "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9,
        "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    # **Permitir que a atividade seja cadastrada sempre**
    if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):
        with st.popover('➕ Registrar Atividade'):
            with st.form("form_adicionar_atividade"):
                st.subheader("➕ Nova Atividade")

                # Criar duas colunas para organizar os campos
                col1, col2 = st.columns(2)

                with col1:
                    tipo = st.selectbox("Tipo de Atividade *", ["","Observação","Whatsapp", "Ligação", "Email", "Linkedin", "Reunião"])
                    titulo = st.text_input("Título *")
                    descricao = st.text_area("Descrição *")

                with col2:
                    status = st.selectbox("Status *", ["", "NA", "Ocupado", "Conectado", "Gatekeeper", "Ligação Positiva", "Ligação Negativa"])
                    contato = st.multiselect("Contato Vinculado *", lista_contatos)  # Mostra apenas os contatos da empresa
                    data_execucao = st.date_input("Data de Execução", value=datetime.today().date())

                # **Configuração da Tarefa Vinculada**
                st.markdown("---")  # Separador visual
                st.subheader("📌 Prazo para o acompanhamento")
                
                titulo_tarefa = "Acompanhar " + tipo #st.text_input("Título da Tarefa", value="Acompanhar " + tipo, disabled=True)
                prazo = st.selectbox("Prazo", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses", "Personalizada"], index=3)
                data_execucao_tarefa = st.date_input("Data de Execução", value=calcular_data_execucao(prazo)) if prazo == "Personalizada" else calcular_data_execucao(prazo)
                    

                observacoes_tarefa = "" #st.text_area("Observações da Tarefa", value="", disabled=True)
                status_tarefa = "🟨 Em andamento"  # Status fixo para a tarefa

                submit_atividade = st.form_submit_button("✅ Adicionar Atividade")

                if submit_atividade:
                    if tipo == 'Observação' and descricao:
                        atividade_id = str(datetime.now().timestamp())  # Gerar um ID único baseado no tempo

                        # Criar a atividade
                        nova_atividade = {
                            "atividade_id": atividade_id,
                            "tipo_atividade": tipo,
                            "status": status,
                            "titulo": titulo,
                            "empresa": empresa_cnpj,
                            "contato": contato,
                            "descricao": descricao,
                            "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
                            "data_criacao_atividade": datetime.now().strftime("%Y-%m-%d")
                        }
                        collection_atividades.insert_one(nova_atividade)

                        st.success("Atividade e tarefa vinculada adicionadas com sucesso! 📌")
                        st.rerun()
                        
                    elif titulo and tipo and status and descricao and contatos_vinculados:
                        atividade_id = str(datetime.now().timestamp())  # Gerar um ID único baseado no tempo

                        # Criar a atividade
                        nova_atividade = {
                            "atividade_id": atividade_id,
                            "tipo_atividade": tipo,
                            "status": status,
                            "titulo": titulo,
                            "empresa": empresa_cnpj,
                            "contato": ", ".join(atividade.get("contato", "")) if isinstance(atividade.get("contato", []), list) else atividade.get("contato", ""),
                            "descricao": descricao,
                            "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
                            "data_criacao_atividade": datetime.now().strftime("%Y-%m-%d")
                        }
                        collection_atividades.insert_one(nova_atividade)
                        # Criar a tarefa vinculada
                        nova_tarefa = {
                            "tarefa_id": str(datetime.now().timestamp()),  # Gerar um ID único baseado no tempo
                            "titulo": titulo_tarefa,
                            "empresa": empresa_cnpj,
                            "atividade_vinculada": atividade_id,  # Relacionar com a atividade criada
                            "data_execucao": data_execucao_tarefa.strftime("%Y-%m-%d"),
                            "status": status_tarefa,
                            "observacoes": observacoes_tarefa
                        }
                        collection_tarefas = get_collection("tarefas")
                        collection_tarefas.insert_one(nova_tarefa)

                        st.success("Atividade e tarefa vinculada adicionadas com sucesso! 📌")
                        st.rerun()
                                
                        
                    else:
                        st.error("Preencha os campos obrigatórios: Tipo, Status, Título, Contato, Descrição e Datas.")



    with st.expander("🗓️ Atividades realizadas por período", expanded=False):

        if atividades:
            atividades_ordenadas = defaultdict(list)

            for atividade in atividades:
                data_execucao = datetime.strptime(atividade["data_execucao_atividade"], "%Y-%m-%d")
                mes_ingles = data_execucao.strftime("%B")  # Nome do mês em inglês
                mes_portugues = MESES_PT.get(mes_ingles, mes_ingles)  # Traduz para PT-BR
                chave_mes_ano = (data_execucao.year, MESES_NUMERICOS[mes_portugues], f"{mes_portugues} {data_execucao.year}")

                atividades_ordenadas[chave_mes_ano].append({
                    "data": data_execucao.strftime("%d/%m/%Y"),
                    "titulo": atividade["titulo"],
                    "tipo": atividade["tipo_atividade"],
                    "contato": ", ".join(atividade["contato"]) if isinstance(atividade["contato"], list) else atividade["contato"],
                    "descricao": atividade["descricao"],
                    "data_execucao_timestamp": data_execucao.timestamp()  # Adiciona timestamp para ordenação dentro do mês
                })

            # Ordenar os blocos de meses do mais recente para o mais antigo
            for (ano, mes_num, mes_ano_str), atividades_lista in sorted(atividades_ordenadas.items(), reverse=True):  # Ordena por ano e mês
                st.subheader(f"📅 {mes_ano_str}")  # Título do mês e ano
                
                # Ordena atividades dentro do mês do mais recente para o mais antigo
                atividades_lista.sort(key=lambda x: x["data_execucao_timestamp"], reverse=True)

                with st.container():
                    for atividade in atividades_lista:
                        st.write(f'**📆 {atividade["data"]}** - **{atividade["titulo"]}**: {atividade["tipo"]} para **{atividade["contato"]}**. 📝 {atividade["descricao"]}')
                    st.write('---')

        else:
            st.warning("Nenhuma atividade cadastrada para esta empresa.")
