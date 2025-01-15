import streamlit as st
from utils.database import get_collection

def gerenciamento_orcamentos():
    st.title("Gerenciamento de Orçamentos")
    collection_orcamentos = get_collection("orcamentos")
    collection_oportunidades = get_collection("oportunidades")  # Coleção de Oportunidades

    # Abas para gerenciar orçamentos
    tab1, tab2, tab3 = st.tabs(["Cadastrar Orçamento", "Remover Orçamento", "Exibir Orçamentos"])

    # Status pré-definidos para orçamento
    status_orcamento = ["Pendente", "Aprovado", "Reprovado", "Enviado", "Cancelado"]

    # Aba: Cadastrar Orçamento
    with tab1:
        st.header("Cadastrar Orçamento")

        # Obter oportunidades cadastradas
        oportunidades = list(collection_oportunidades.find({}, {"_id": 0, "cliente": 1, "produto": 1, "valor_estimado": 1}))
        opcoes_oportunidades = [
            f"Cliente: {o['cliente']}, Produto: {o['produto']}, Valor Estimado: R${o['valor_estimado']:.2f}"
            for o in oportunidades
        ]

        if not oportunidades:
            st.warning("Nenhuma oportunidade encontrada. Cadastre uma oportunidade antes de adicionar orçamentos.")
        else:
            with st.form(key="form_cadastro_orcamento"):
                oportunidade = st.selectbox("Oportunidade Associada", options=opcoes_oportunidades, key="select_oportunidade_orcamento")
                sel_desconto = st.number_input("Percentual de Desconto (%)", min_value=0.0, max_value=100.0, step=0.5, key="input_sel_desconto_orcamento")
                data_envio = st.date_input("Data de Envio", key="input_data_envio_orcamento")
                data_status = st.date_input("Data do Status", key="input_data_status_orcamento")
                status_orcamento_selecionado = st.selectbox("Status do Orçamento", options=status_orcamento, key="select_status_orcamento")

                submit = st.form_submit_button("Cadastrar")

                if submit:
                    if oportunidade:
                        # Obter a oportunidade selecionada
                        oportunidade_selecionada = next(
                            (o for o in oportunidades if f"Cliente: {o['cliente']}, Produto: {o['produto']}, Valor Estimado: R${o['valor_estimado']:.2f}" == oportunidade), None
                        )

                        if oportunidade_selecionada:
                            # Criar o documento do orçamento
                            document = {
                                "oportunidade": oportunidade_selecionada,
                                "sel_desconto": sel_desconto,
                                "data_envio": str(data_envio),  # Converter para string
                                "data_status": str(data_status),  # Converter para string
                                "status_orcamento": status_orcamento_selecionado,
                            }
                            collection_orcamentos.insert_one(document)
                            st.success("Orçamento cadastrado com sucesso!")
                        else:
                            st.error("Erro ao localizar a oportunidade selecionada. Por favor, tente novamente.")
                    else:
                        st.error("Selecione uma oportunidade para continuar.")

    # Aba: Remover Orçamento
    with tab2:
        st.header("Remover Orçamento")
        with st.form(key="form_remover_orcamento"):
            remove_id = st.text_input("ID do Orçamento a Remover", key="input_remover_orcamento_id")
            remove_submit = st.form_submit_button("Remover Orçamento")

            if remove_submit:
                if remove_id:
                    # Remover o orçamento pelo ID
                    result = collection_orcamentos.delete_one({"_id": remove_id})
                    if result.deleted_count > 0:
                        st.success(f"Orçamento com ID '{remove_id}' removido com sucesso!")
                    else:
                        st.error(f"Nenhum orçamento encontrado com o ID '{remove_id}'.")
                else:
                    st.error("Por favor, insira o ID do orçamento para remover.")

    # Aba: Exibir Orçamentos
    with tab3:
        st.header("Orçamentos Cadastrados")
        if st.button("Carregar Orçamentos", key="botao_carregar_orcamentos"):
            orcamentos = list(collection_orcamentos.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if orcamentos:
                st.write("Lista de Orçamentos:")
                for orcamento in orcamentos:
                    st.write(
                        f"Oportunidade: {orcamento['oportunidade']}, Seleção de Desconto: {orcamento['sel_desconto']}%, "
                        f"Data de Envio: {orcamento['data_envio']}, Data de Status: {orcamento['data_status']}, "
                        f"Status: {orcamento['status_orcamento']}"
                    )
            else:
                st.write("Nenhum orçamento cadastrado ainda.")
