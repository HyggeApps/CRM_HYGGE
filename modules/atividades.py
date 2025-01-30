from utils.database import get_collection
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import defaultdict

# Dicionário de meses em português
MESES_PT = {
    "January": "Janeiro", "February": "Fevereiro", "March": "Março",
    "April": "Abril", "May": "Maio", "June": "Junho",
    "July": "Julho", "August": "Agosto", "September": "Setembro",
    "October": "Outubro", "November": "Novembro", "December": "Dezembro"
}

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

    with st.expander("🗓️ Atividades realizadas por período", expanded=True):
        if atividades:
            atividades_ordenadas = defaultdict(list)

            for atividade in atividades:
                data_execucao = datetime.strptime(atividade["data_execucao_atividade"], "%Y-%m-%d")
                mes_ingles = data_execucao.strftime("%B")  # Nome do mês em inglês
                mes_portugues = MESES_PT.get(mes_ingles, mes_ingles)  # Traduz para PT-BR
                chave_mes_ano = f"{mes_portugues} {data_execucao.strftime('%Y')}"  # Exemplo: "Janeiro 2025"

                atividades_ordenadas[chave_mes_ano].append({
                    "data": data_execucao.strftime("%d/%m/%Y"),
                    "titulo": atividade["titulo"],
                    "tipo": atividade["tipo_atividade"],
                    "contato": ", ".join(atividade["contato"]) if isinstance(atividade["contato"], list) else atividade["contato"],
                    "descricao": atividade["descricao"]
                })

            # Criar um bloco separado para cada mês dentro do `st.expander()`
            for mes_ano, atividades_lista in sorted(atividades_ordenadas.items(), reverse=True):  # Ordena do mais recente para o mais antigo
                st.subheader(f"📅 {mes_ano}")  # Título do mês e ano
                with st.container():
                    for atividade in atividades_lista:
                        st.write(f'**📆 {atividade["data"]}** - **{atividade["titulo"]}**: {atividade["tipo"]} para **{atividade["contato"]}**. 📝 {atividade["descricao"]}')
                    st.write('---')

        else:
            st.warning("Nenhuma atividade cadastrada para esta empresa.")


    # **Permitir que a atividade seja cadastrada sempre**
    if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):
        with st.popover('➕ Registrar Atividade'):
            with st.form("form_adicionar_atividade"):
                st.subheader("➕ Nova Atividade")
                tipo = st.selectbox("Tipo de Atividade *", ["", "Whatsapp", "Ligação", "Email", "Linkedin", "Reunião"])
                status = st.selectbox("Status *", ["", "NA", "Ocupado", "Conectado", "Gatekeeper", "Ligação Positiva", "Ligação Negativa"])
                titulo = st.text_input("Título *")
                contato = st.multiselect("Contato Vinculado *", lista_contatos)  # Mostra apenas os contatos da empresa
                descricao = st.text_area("Descrição *")

                # Definir data de criação como hoje
                data_criacao = datetime.today().date()
                # Criar campo de data de execução com sugestão
                data_execucao = st.date_input("Data de Execução", value=data_criacao)

                submit_atividade = st.form_submit_button("✅ Adicionar Atividade")

                if submit_atividade:
                    if titulo and tipo and status and descricao and contatos_vinculados:
                        atividade_id = str(datetime.now().timestamp())  # Gerar um ID único baseado no tempo
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
                        st.success("Atividade adicionada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios: Tipo, Status, Título, Contato, Descrição e Datas.")
