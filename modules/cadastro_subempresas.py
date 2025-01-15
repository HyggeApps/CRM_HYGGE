import streamlit as st
from utils.database import get_collection

def gerenciamento_subempresas():
    st.title("Gerenciamento de SubEmpresas")
    collection_empresas = get_collection("empresas")  # Coleção de Empresas Matriz
    collection_subempresas = get_collection("subempresas")  # Coleção de SubEmpresas

    # Abas para gerenciar subempresas
    tab1, tab2, tab3 = st.tabs(["Cadastrar SubEmpresa", "Remover SubEmpresa", "Exibir SubEmpresas"])

    # Aba: Cadastrar SubEmpresa
    with tab1:
        st.header("Cadastrar SubEmpresa")

        # Obter empresas matriz cadastradas
        empresas_matriz = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1, "usuario": 1}))
        opcoes_matriz = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas_matriz]  # Lista de opções para selectbox

        if not empresas_matriz:
            st.warning("Nenhuma empresa matriz encontrada. Cadastre uma empresa matriz primeiro antes de adicionar subempresas.")
        else:
            with st.form(key="form_cadastro_subempresa"):
                empresa_matriz = st.selectbox("Empresa Matriz", options=opcoes_matriz, key="select_empresa_matriz")
                razao_social = st.text_input("Razão Social da SubEmpresa", key="input_razao_social_subempresa")
                cnpj = st.text_input("CNPJ da SubEmpresa", key="input_cnpj_subempresa")
                rua = st.text_input("Rua", key="input_rua_subempresa")
                cep = st.text_input("CEP", key="input_cep_subempresa")
                bairro = st.text_input("Bairro", key="input_bairro_subempresa")
                cidade = st.text_input("Cidade", key="input_cidade_subempresa")
                estado = st.text_input("Estado", key="input_estado_subempresa")
                fone = st.text_input("Telefone", key="input_fone_subempresa")
                insc_estadual = st.text_input("Inscrição Estadual", key="input_insc_estadual_subempresa")
                documentos = st.file_uploader("Documentos", accept_multiple_files=True, key="input_documentos_subempresa")

                submit = st.form_submit_button("Cadastrar")

                if submit:
                    if razao_social and cnpj and empresa_matriz:
                        # Obter dados da empresa matriz selecionada
                        matriz_selecionada = next((e for e in empresas_matriz if f"{e['razao_social']} (CNPJ: {e['cnpj']})" == empresa_matriz), None)
                        if matriz_selecionada:
                            usuario_herdado = matriz_selecionada["usuario"]  # Herdar usuário da Matriz

                            # Verificar duplicidade no banco de subempresas
                            existing_subempresa = collection_subempresas.find_one({"cnpj": cnpj})
                            if existing_subempresa:
                                st.error("SubEmpresa já cadastrada com este CNPJ!")
                            else:
                                # Processar documentos
                                documentos_salvos = []
                                if documentos:
                                    for doc in documentos:
                                        documentos_salvos.append({"nome_documento": doc.name, "tipo": doc.type})

                                # Criar o documento da subempresa
                                document = {
                                    "empresa_matriz": matriz_selecionada["cnpj"],  # Vincular à matriz pelo CNPJ
                                    "razao_social": razao_social,
                                    "cnpj": cnpj,
                                    "rua": rua,
                                    "cep": cep,
                                    "bairro": bairro,
                                    "cidade": cidade,
                                    "estado": estado,
                                    "fone": fone,
                                    "insc_estadual": insc_estadual,
                                    "usuario": usuario_herdado,  # Herdar o usuário da matriz
                                    "documentos": documentos_salvos,
                                }
                                collection_subempresas.insert_one(document)
                                st.success("SubEmpresa cadastrada com sucesso!")
                        else:
                            st.error("Erro ao localizar a empresa matriz selecionada. Por favor, tente novamente.")
                    else:
                        st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ, Empresa Matriz).")

    # Aba: Remover SubEmpresa
    with tab2:
        st.header("Remover SubEmpresa")
        with st.form(key="form_remover_subempresa"):
            remove_cnpj = st.text_input("CNPJ da SubEmpresa a Remover", key="input_remover_cnpj_subempresa")
            remove_submit = st.form_submit_button("Remover SubEmpresa")

            if remove_submit:
                if remove_cnpj:
                    # Verificar se a subempresa existe e remover
                    result = collection_subempresas.delete_one({"cnpj": remove_cnpj})
                    if result.deleted_count > 0:
                        st.success(f"SubEmpresa com CNPJ '{remove_cnpj}' removida com sucesso!")
                    else:
                        st.error(f"Nenhuma subempresa encontrada com o CNPJ '{remove_cnpj}'.")
                else:
                    st.error("Por favor, insira o CNPJ da subempresa para remover.")

    # Aba: Exibir SubEmpresas
    with tab3:
        st.header("SubEmpresas Cadastradas")
        if st.button("Carregar SubEmpresas", key="botao_carregar_subempresas"):
            subempresas = list(collection_subempresas.find({}, {"_id": 0}))  # Excluir o campo "_id" ao exibir
            if subempresas:
                st.write("Lista de SubEmpresas:")
                for subempresa in subempresas:
                    st.write(
                        f"Razão Social: {subempresa['razao_social']}, CNPJ: {subempresa['cnpj']}, "
                        f"Vinculada à Matriz (CNPJ): {subempresa['empresa_matriz']}, "
                        f"Endereço: {subempresa['rua']}, {subempresa['bairro']}, {subempresa['cidade']}, {subempresa['estado']}, "
                        f"Telefone: {subempresa['fone']}, Usuário Associado: {subempresa['usuario']}"
                    )
            else:
                st.write("Nenhuma subempresa cadastrada ainda.")
