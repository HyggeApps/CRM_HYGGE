import streamlit as st
from utils.database import get_collection

def gerenciamento_leads():
    st.title("Gerenciamento de Leads")
    collection_leads = get_collection("leads")
    collection_empresas = get_collection("empresas")  # Coleção de Empresas
    collection_contatos = get_collection("contatos")  # Coleção de Contatos

    # Abas para gerenciar leads
    tab1, tab2, tab3 = st.tabs(["Cadastrar Lead", "Remover Lead", "Exibir Leads"])

    # Aba: Cadastrar Lead
    with tab1:
        st.header("Cadastrar Lead")

        # Obter empresas e contatos cadastrados
        empresas = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
        contatos = list(collection_contatos.find({}, {"_id": 0, "nome": 1, "sobrenome": 1, "email": 1}))

        opcoes_empresas = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas]
        opcoes_contatos = [f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos]

        if not empresas:
            st.warning("Nenhuma empresa encontrada. Cadastre uma empresa antes de adicionar leads.")
        elif not contatos:
            st.warning("Nenhum contato encontrado. Cadastre um contato antes de adicionar leads.")
        else:
            with st.form(key="form_cadastro_lead"):
                empresa = st.selectbox("Empresa Associada", options=opcoes_empresas, key="select_empresa_lead")
                contato = st.selectbox("Contato Associado", options=opcoes_contatos, key="select_contato_lead")
                conteudo = st.text_area("Conteúdo do Lead", key="input_conteudo_lead")
                data_contato = st.date_input("Data do Contato", key="input_data_contato_lead")
                data_prox_contato = st.date_input("Data do Próximo Contato", key="input_data_prox_contato_lead")
                status_oportunidade = st.selectbox(
                    "Status da Oportunidade", 
                    ["Aberta", "Em Progresso", "Concluída", "Perdida"], 
                    key="select_status_oportunidade_lead"
                )
                tipo_lead = st.selectbox("Tipo de Lead", ["Quente", "Morno", "Frio"], key="select_tipo_lead")
                rotulo = st.text_input("Rótulo do Lead", key="input_rotulo_lead")

                submit = st.form_submit_button("Cadastrar")

                if submit:
                    if empresa and contato and conteudo:
                        # Obter dados da empresa e do contato selecionados
                        empresa_selecionada = next((e for e in empresas if f"{e['razao_social']} (CNPJ: {e['cnpj']})" == empresa), None)
                        contato_selecionado = next((c for c in contatos if f"{c['nome']} {c['sobrenome']} ({c['email']})" == contato), None)

                        if empresa_selecionada and contato_selecionado:
                            # Criar o documento do lead
                            document = {
                                "empresa": empresa_selecionada["cnpj"],  # Vincular ao CNPJ da empresa
                                "contato": contato_selecionado["email"],  # Vincular ao email do contato
                                "conteudo": conteudo,
                                "data_contato": str(data_contato),  # Converter data para string
                                "data_prox_contato": str(data_prox_contato),  # Converter data para string
                                "status_oportunidade": status_oportunidade,
                                "tipo_lead": tipo_lead,
                                "rotulo": rotulo,
                            }
                            collection_leads.insert_one(document)
                            st.success("Lead cadastrado com sucesso!")
                        else:
                            st.error("Erro ao localizar a empresa ou contato selecionados. Por favor, tente novamente.")
                    else:
                        st.error("Preencha todos os campos obrigatórios (Empresa, Contato, Conteúdo).")

    # Aba: Remover Lead
    with tab2:
        st.header("Remover Lead")
        with st.form(key="form_remover_lead"):
            remove_lead_id = st.text_input("ID do Lead a Remover", key="input_remover_lead_id")
            remove_submit = st.form_submit_button("Remover Lead")

            if remove_submit:
                if remove_lead_id:
                    # Verificar se o lead existe e remover
                    result = collection_leads.delete_one({"_id": remove_lead_id})
                    if result.deleted_count > 0:
                        st.success(f"Lead com ID '{remove_lead_id}' removido com sucesso!")
                    else:
                        st.error(f"Nenhum lead encontrado com o ID '{remove_lead_id}'.")
                else:
                    st.error("Por favor, insira o ID do lead para remover.")

    # Aba: Exibir Leads
    with tab3:
        st.header("Leads Cadastrados")
        if st.button("Carregar Leads", key="botao_carregar_leads"):
            leads = list(collection_leads.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if leads:
                st.write("Lista de Leads:")
                for lead in leads:
                    st.write(
                        f"Empresa: {lead['empresa']}, Contato: {lead['contato']}, Conteúdo: {lead['conteudo']}, "
                        f"Data do Contato: {lead['data_contato']}, Data do Próximo Contato: {lead['data_prox_contato']}, "
                        f"Status: {lead['status_oportunidade']}, Tipo: {lead['tipo_lead']}, Rótulo: {lead['rotulo']}"
                    )
            else:
                st.write("Nenhum lead cadastrado ainda.")
