import streamlit as st
from utils.database import get_collection
import pandas as pd

# ========================== #
#      ADICIONAR CONTATO     #
# ========================== #
def adicionar_contato(user, admin):
    st.header("➕ Cadastrar Contato")

    collection_contatos = get_collection("contatos")
    collection_empresas = get_collection("empresas")
    collection_subempresas = get_collection("subempresas")

    empresas = list(collection_empresas.find({"usuario": user}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
    subempresas = list(collection_subempresas.find({"usuario": user}, {"_id": 0, "razao_social": 1, "cnpj": 1}))

    entidades = [{"nome": e["razao_social"], "cnpj": e["cnpj"], "tipo": "Empresa"} for e in empresas]
    entidades += [{"nome": s["razao_social"], "cnpj": s["cnpj"], "tipo": "SubEmpresa"} for s in subempresas]

    opcoes_entidades = [''] + [f"{e['nome']} (CNPJ: {e['cnpj']}) [{e['tipo']}]" for e in entidades]

    if not entidades:
        st.warning("Cadastre uma empresa antes de adicionar contatos.")
    else:
        empresa = st.selectbox("Empresa ou SubEmpresa Associada", options=opcoes_entidades)
        if empresa != '':
            with st.form(key="form_cadastro_contato"):
                nome = st.text_input("Nome do Contato")
                sobrenome = st.text_input("Sobrenome do Contato")
                email = st.text_input("Email")
                fone = st.text_input("Telefone")
                linkedin = st.text_input("LinkedIn")
                setor = st.text_input("Setor")

                submit = st.form_submit_button("Cadastrar")

                if submit:
                    entidade_selecionada = next((e for e in entidades if f"{e['nome']} (CNPJ: {e['cnpj']}) [{e['tipo']}]" == empresa), None)
                    if entidade_selecionada:
                        document = {
                            "nome": nome,
                            "sobrenome": sobrenome,
                            "email": email,
                            "fone": fone,
                            "linkedin": linkedin,
                            "setor": setor,
                            "empresa": entidade_selecionada["cnpj"],
                            "tipo_empresa": entidade_selecionada["tipo"],
                        }
                        collection_contatos.insert_one(document)
                        st.success("Contato cadastrado com sucesso!")

# ========================== #
#      EDITAR CONTATO        #
# ========================== #
def editar_contato(user, admin):
    st.header("✏️ Editar Contato")

    collection_contatos = get_collection("contatos")

    contatos = list(collection_contatos.find({}, {"_id": 0, "email": 1, "nome": 1, "sobrenome": 1}))

    if not contatos:
        st.warning("Nenhum contato encontrado.")
    else:
        contato_selecionado = st.selectbox("Selecione um contato para editar", [f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos])
        email_editar = contato_selecionado.split("(")[-1].strip(")")

        contato_dados = collection_contatos.find_one({"email": email_editar}, {"_id": 0})

        if contato_dados:
            with st.form(key="form_editar_contato"):
                nome = st.text_input("Nome", value=contato_dados.get("nome", ""))
                sobrenome = st.text_input("Sobrenome", value=contato_dados.get("sobrenome", ""))
                fone = st.text_input("Telefone", value=contato_dados.get("fone", ""))

                submit = st.form_submit_button("Salvar Alterações")
                if submit:
                    collection_contatos.update_one({"email": email_editar}, {"$set": {"nome": nome, "sobrenome": sobrenome, "fone": fone}})
                    st.success("Contato atualizado!")

# ========================== #
#      REMOVER CONTATO       #
# ========================== #
def remover_contato(user, admin):
    st.header("🗑️ Remover Contato")

    email = st.text_input("Digite o email do contato a remover")
    if st.button("Remover"):
        collection_contatos = get_collection("contatos")
        result = collection_contatos.delete_one({"email": email})
        if result.deleted_count > 0:
            st.success("Contato removido!")
        else:
            st.error("Contato não encontrado.")


def exibir_contatos_empresa(user, admin, empresa_cnpj):
    """
    Exibe contatos vinculados à empresa selecionada, permitindo adicionar, editar e remover contatos
    se o usuário for o proprietário da empresa ou admin.
    """
    collection_contatos = get_collection("contatos")

    # Buscar contatos vinculados à empresa selecionada
    contatos = list(collection_contatos.find({"empresa": empresa_cnpj}, {"_id": 0}))

    with st.expander("📞 Contatos", expanded=True):
        if contatos:
            df_contatos = pd.DataFrame(contatos)

            # Renomear colunas para exibição
            df_contatos = df_contatos.rename(
                columns={
                    "nome": "Nome",
                    "sobrenome": "Sobrenome",
                    "cargo": "Cargo",
                    "email": "E-mail",
                    "fone": "Telefone"
                }
            )

            # Reorganizar colunas
            df_contatos = df_contatos[["Nome", "Sobrenome", "Cargo", "E-mail", "Telefone"]]

            # Exibir tabela
            st.dataframe(df_contatos, hide_index=True, use_container_width=True)

        else:
            st.warning("Nenhum contato cadastrado para esta empresa.")

        # Verifica permissão para editar ou adicionar contatos
        if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):
            st.write("### ➕ Gerenciar Contatos")

            # Opção para adicionar um novo contato
            with st.form("form_adicionar_contato"):
                st.subheader("Adicionar Contato")
                nome = st.text_input("Nome")
                sobrenome = st.text_input("Sobrenome")
                cargo = st.text_input("Cargo")
                email = st.text_input("E-mail")
                telefone = st.text_input("Telefone")

                submit_adicionar = st.form_submit_button("Adicionar Contato")

                if submit_adicionar:
                    if nome and email:
                        collection_contatos.insert_one({
                            "nome": nome,
                            "sobrenome": sobrenome,
                            "cargo": cargo,
                            "email": email,
                            "fone": telefone,
                            "empresa": empresa_cnpj
                        })
                        st.success("Contato adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios: Nome e E-mail.")

            # Se houver contatos cadastrados, exibir opções de edição/remoção
            if contatos:
                contato_selecionado = st.selectbox(
                    "Selecione um contato para editar/remover",
                    options=[f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos]
                )

                if contato_selecionado:
                    email_editar = contato_selecionado.split("(")[-1].strip(")")

                    contato_dados = collection_contatos.find_one({"email": email_editar}, {"_id": 0})

                    if contato_dados:
                        with st.form("form_editar_contato"):
                            st.subheader("✏️ Editar Contato")
                            nome_edit = st.text_input("Nome", value=contato_dados.get("nome", ""))
                            sobrenome_edit = st.text_input("Sobrenome", value=contato_dados.get("sobrenome", ""))
                            cargo_edit = st.text_input("Cargo", value=contato_dados.get("cargo", ""))
                            email_edit = st.text_input("E-mail", value=contato_dados.get("email", ""), disabled=True)
                            telefone_edit = st.text_input("Telefone", value=contato_dados.get("fone", ""))

                            submit_editar = st.form_submit_button("Salvar Alterações")
                            if submit_editar:
                                collection_contatos.update_one(
                                    {"email": email_editar},
                                    {"$set": {
                                        "nome": nome_edit,
                                        "sobrenome": sobrenome_edit,
                                        "cargo": cargo_edit,
                                        "fone": telefone_edit
                                    }}
                                )
                                st.success("Contato atualizado com sucesso!")
                                st.rerun()

                        if st.button("🗑️ Remover Contato"):
                            collection_contatos.delete_one({"email": email_editar})
                            st.success(f"Contato {contato_selecionado} removido com sucesso!")
                            st.rerun()
