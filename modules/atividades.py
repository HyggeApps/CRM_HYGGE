import streamlit as st
from utils.database import get_collection
from datetime import datetime
from collections import defaultdict

def exibir_atividades_empresa(user, admin, empresa_cnpj):
    collection_atividades = get_collection("atividades")
    collection_contatos = get_collection("contatos")

    # Buscar contatos vinculados à empresa
    contatos_vinculados = list(collection_contatos.find({"empresa": empresa_cnpj}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))

    # Criar lista de contatos formatada
    lista_contatos = [""] + [f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos_vinculados]

    # Buscar atividades vinculadas à empresa selecionada
    atividades = list(collection_atividades.find({"empresa": empresa_cnpj}, {"_id": 0}))

    # Adicionar nova atividade (Apenas se o usuário for admin ou proprietário)
    if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):
        with st.popover('➕ Adicionar Atividade'):
            st.write(2)
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

    # Exibir atividades em formato de timeline
    if atividades:
        atividades_ordenadas = defaultdict(list)
        for atividade in atividades:
            data_execucao = datetime.strptime(atividade["data_execucao_atividade"], "%Y-%m-%d")
            chave_mes_ano = data_execucao.strftime("%B %Y")  # Exemplo: "Janeiro 2025"
            atividades_ordenadas[chave_mes_ano].append({
                "data": data_execucao.strftime("%d/%m/%Y"),
                "titulo": atividade["titulo"],
                "tipo": atividade["tipo_atividade"],
                "contato": ", ".join(atividade["contato"]) if isinstance(atividade["contato"], list) else atividade["contato"],
                "descricao": atividade["descricao"]
            })

        with st.expander("📌 Histórico de Atividades", expanded=True):
            for mes_ano, atividades_lista in sorted(atividades_ordenadas.items(), reverse=True):  # Ordena do mês mais recente para o mais antigo
                st.markdown(f"### 📅 {mes_ano}")  # Título do mês e ano
                for atividade in atividades_lista:
                    with st.container():
                        st.markdown(f"""
                        **📆 {atividade['data']}**  
                        **🔹 {atividade['titulo']}**: {atividade['tipo']} para **{atividade['contato']}**  
                        📝 {atividade['descricao']}
                        ---
                        """)
    else:
        st.warning("Nenhuma atividade cadastrada para esta empresa.")

