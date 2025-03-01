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
    """Calcula a data de execução da tarefa com base na opção selecionada, considerando apenas dias úteis."""
    hoje = datetime.today().date()
    
    def adicionar_dias_uteis(dias):
        """Adiciona um número de dias úteis à data de hoje, ignorando finais de semana."""
        data = hoje
        while dias > 0:
            data += timedelta(days=1)
            if data.weekday() < 5:  # Apenas segunda a sexta-feira (0=Segunda, ..., 4=Sexta)
                dias -= 1
        return data

    opcoes_prazo = {
        "Hoje": hoje,
        "1 dia útil": adicionar_dias_uteis(1),  # Agora considera apenas dias úteis
        "2 dias úteis": adicionar_dias_uteis(2),
        "3 dias úteis": adicionar_dias_uteis(3),
        "1 semana": hoje + timedelta(weeks=1),
        "2 semanas": hoje + timedelta(weeks=2),
        "1 mês": hoje + timedelta(days=30),
        "2 meses": hoje + timedelta(days=60),
        "3 meses": hoje + timedelta(days=90)
    }
    
    return opcoes_prazo.get(opcao, hoje)

@st.fragment
def exibir_atividades_empresa(user, admin, empresa_nome):
    collection_atividades = get_collection("atividades")
    collection_contatos = get_collection("contatos")

    if not empresa_nome:
        st.error("Erro: Nenhuma empresa selecionada para exibir atividades.")
        return

    # Buscar contatos vinculados à empresa
    contatos_vinculados = list(collection_contatos.find({"empresa": empresa_nome}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))

    # Criar lista de contatos formatada
    lista_contatos = [""] + [f"{c['nome']} {c['sobrenome']}" for c in contatos_vinculados]

    # Buscar atividades vinculadas **somente** à empresa selecionada
    atividades = list(collection_atividades.find({"empresa": empresa_nome}, {"_id": 0}))

    # Dicionário de meses com valores numéricos para ordenação
    MESES_NUMERICOS = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3,
        "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9,
        "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    # **Permitir que a atividade seja cadastrada sempre**
    if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):
        def criar_form_observacao(key):
            with st.form(key):
                st.subheader("🟫➕ Observação")
                st.info('Registrar uma **observação** nas atividades da empresa.')
                contato = st.multiselect("Contato Vinculado", lista_contatos)  # Mostra apenas os contatos da empresa
            
                data_execucao = st.date_input("Data de Execução", value=datetime.today().date())
                
                descricao = st.text_area("Descrição *")
                # **Configuração da Tarefa Vinculada**
                st.markdown("---")  # Separador visual
                st.subheader("📌 Prazo para o acompanhamento")
                
                prazo = st.selectbox("Prazo", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"], index=3)
                data_execucao_tarefa = st.date_input("Data de Execução", value=calcular_data_execucao(prazo)) if prazo == "Personalizada" else calcular_data_execucao(prazo)

                submit_atividade = st.form_submit_button("✅ Adicionar Atividade")

                if submit_atividade:
                        
                    if descricao:
                        atividade_id = str(datetime.now().timestamp())  # Gerar um ID único baseado no tempo

                        # Criar a atividade
                        nova_atividade = {
                            "atividade_id": atividade_id,
                            "tipo_atividade": "Observação",
                            "empresa": empresa_nome,
                            "contato": contato,
                            "descricao": descricao,
                            "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
                            "data_criacao_atividade": datetime.now().strftime("%Y-%m-%d")
                        }
                        collection_atividades.insert_one(nova_atividade)
                        # Criar a tarefa vinculada
                        nova_tarefa = {
                            "tarefa_id": str(datetime.now().timestamp()),  # Gerar um ID único baseado no tempo
                            "titulo": "Observação",
                            "empresa": empresa_nome,
                            "atividade_vinculada": atividade_id,  # Relacionar com a atividade criada
                            "data_execucao": data_execucao_tarefa.strftime("%Y-%m-%d"),
                            "status": "🟨 Em andamento",
                            "observacoes": ""
                        }
                        collection_tarefas = get_collection("tarefas")
                        collection_tarefas.insert_one(nova_tarefa)

                        # 🔄 Atualizar a última atividade da empresa
                        data_hoje = datetime.now().strftime("%Y-%m-%d")  # Data atual
                        collection_empresas = get_collection("empresas")
                        collection_empresas.update_one(
                            {"razao_social": empresa_nome},
                            {"$set": {"ultima_atividade": data_hoje}}
                        )

                        st.success("Atividade e tarefa vinculada adicionadas com sucesso! 📌")
                        st.rerun()       
                        
                    else:
                        st.error("Preencha os campos obrigatórios: Descrição.")

        # Função para formulário de Whatsapp
        def criar_form_whatsapp(key):
            with st.form(key):
                st.subheader("🟩➕ Whatsapp")
                mensagem = st.text_area("Mensagem de Whatsapp", key=f"mensagem_{key}")
                submit = st.form_submit_button("Adicionar Whatsapp")
            return {"submit": submit, "mensagem": mensagem}

        # Função para formulário de Ligação
        def criar_form_ligacao(key):
            with st.form(key):
                st.subheader("🟨➕ Ligação")
                duracao = st.text_input("Duração da Ligação (min)", key=f"duracao_{key}")
                observacao = st.text_area("Observações da Ligação", key=f"observacao_{key}")
                submit = st.form_submit_button("Adicionar Ligação")
            return {"submit": submit, "duracao": duracao, "observacao": observacao}

        # Função para formulário de Email
        def criar_form_email(key):
            with st.form(key):
                st.subheader("🟥➕ Email")
                assunto = st.text_input("Assunto do Email", key=f"assunto_{key}")
                conteudo = st.text_area("Conteúdo do Email", key=f"conteudo_{key}")
                submit = st.form_submit_button("Adicionar Email")
            return {"submit": submit, "assunto": assunto, "conteudo": conteudo}

        # Função para formulário de Linkedin
        def criar_form_linkedin(key):
            with st.form(key):
                st.subheader("🟦➕ Linkedin")
                status = st.selectbox(
                    "Status",
                    ["", "Observação", "Bounced", "Sem Resposta", "Email enviado", "Ocupado", "Gatekeeper", "Ligação Positiva", "Ligação Negativa"],
                    key=f"status_{key}"
                )
                submit = st.form_submit_button("Adicionar Linkedin")
            return {"submit": submit, "status": status}

        # Exemplo de uso dos formulários em colunas
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            with st.popover("🟫➕ Obs."):
                form_obs = criar_form_observacao("form_adicionar_observacoes")

        with col2:
            with st.popover("🟩➕ Whatsapp"):
                form_whatsapp = criar_form_whatsapp("form_adicionar_whatsapp")
                if form_whatsapp["submit"]:
                    # Processamento do formulário de Whatsapp.
                    st.success("Whatsapp adicionado!")

        with col3:
            with st.popover("🟨➕ Ligação"):
                form_ligacao = criar_form_ligacao("form_adicionar_ligacao")
                if form_ligacao["submit"]:
                    # Processamento do formulário de Ligação.
                    st.success("Ligação adicionada!")

        with col4:
            with st.popover("🟥➕ Email"):
                form_email = criar_form_email("form_adicionar_email")
                if form_email["submit"]:
                    # Processamento do formulário de Email.
                    st.success("Email adicionado!")

        with col5:
            with st.popover("🟦➕ Linkedin"):
                form_linkedin = criar_form_linkedin("form_adicionar_linkedin")
                if form_linkedin["submit"]:
                    # Processamento do formulário de Linkedin.
                    st.success("Registro no Linkedin adicionado!")
        
        with col6:
            with st.popover('🟪➕ Reunião'):
                st.header('➕ Registro de reunião')
                with st.form("form_adicionar_reuniao"):
                    st.info('Registrar uma **reunião** nas atividades da empresa.')
                    contato = st.multiselect("Contato Vinculado *", lista_contatos)  # Mostra apenas os contatos da empresa
                    
                    status = st.selectbox("Status", ["Realizada", "Contato não apareceu", "Remarcada"])
                    
                    negocio = st.selectbox("Negócio associado à reunião", options=['1','2'])

                    data_execucao = st.date_input("Data de Execução", value=datetime.today().date())
                    
                    descricao = st.text_area("Descrição *")
                    # **Configuração da Tarefa Vinculada**
                    st.markdown("---")  # Separador visual
                    st.subheader("📌 Prazo para o acompanhamento")
                    
                    titulo_tarefa = "Acompanhar Reunião" #st.text_input("Título da Tarefa", value="Acompanhar " + tipo, disabled=True)
                    prazo = st.selectbox("Prazo", ["1 dia útil", "2 dias úteis", "3 dias úteis", "1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"], index=3)
                    data_execucao_tarefa = st.date_input("Data de Execução", value=calcular_data_execucao(prazo)) if prazo == "Personalizada" else calcular_data_execucao(prazo)
                        

                    observacoes_tarefa = "" #st.text_area("Observações da Tarefa", value="", disabled=True)
                    status_tarefa = "🟨 Em andamento"  # Status fixo para a tarefa

                    submit_atividade = st.form_submit_button("✅ Adicionar Atividade")

                    if submit_atividade:
                            
                        if descricao and contatos_vinculados:
                            atividade_id = str(datetime.now().timestamp())  # Gerar um ID único baseado no tempo

                            # Criar a atividade
                            nova_atividade = {
                                "atividade_id": atividade_id,
                                "tipo_atividade": "Reunião",
                                "status": status,
                                "empresa": empresa_nome,
                                "contato": contato,
                                "descricao": descricao,
                                "data_execucao_atividade": data_execucao.strftime("%Y-%m-%d"),
                                "data_criacao_atividade": datetime.now().strftime("%Y-%m-%d")
                            }
                            collection_atividades.insert_one(nova_atividade)
                            # Criar a tarefa vinculada
                            nova_tarefa = {
                                "tarefa_id": str(datetime.now().timestamp()),  # Gerar um ID único baseado no tempo
                                "titulo": titulo_tarefa,
                                "empresa": empresa_nome,
                                "atividade_vinculada": atividade_id,  # Relacionar com a atividade criada
                                "data_execucao": data_execucao_tarefa.strftime("%Y-%m-%d"),
                                "status": status_tarefa,
                                "observacoes": observacoes_tarefa
                            }
                            collection_tarefas = get_collection("tarefas")
                            collection_tarefas.insert_one(nova_tarefa)

                            # 🔄 Atualizar a última atividade da empresa
                            data_hoje = datetime.now().strftime("%Y-%m-%d")  # Data atual
                            collection_empresas = get_collection("empresas")
                            collection_empresas.update_one(
                                {"razao_social": empresa_nome},
                                {"$set": {"ultima_atividade": data_hoje}}
                            )

                            st.success("Atividade e tarefa vinculada adicionadas com sucesso! 📌")
                            st.rerun()       
                            
                        else:
                            st.error("Preencha os campos obrigatórios: Tipo, Título, Contato, Descrição e Datas.")



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
                    "tipo": atividade["tipo_atividade"],
                    "contato": ", ".join(atividade.get("contato", "")) if isinstance(atividade.get("contato", []), list) else atividade.get("contato", ""),
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
                        if atividade["tipo"] != 'Observação':
                            st.write(f'**📆 {atividade["data"]}** - **{atividade["tipo"]}**: **{atividade["contato"]}**. 📝 {atividade["descricao"]}')
                        else:
                            st.write(f'**📆 {atividade["data"]}** - **{atividade["tipo"]}**: **{atividade["contato"]}**. 📝 {atividade["descricao"]}')

                    st.write('---')

        else:
            st.warning("Nenhuma atividade cadastrada para esta empresa.")