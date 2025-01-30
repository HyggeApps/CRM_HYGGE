import streamlit as st
from utils.database import get_collection
import pandas as pd

def exibir_contatos_empresa(user, admin, empresa_cnpj):
    collection_contatos = get_collection("contatos")

    # Buscar apenas os contatos vinculados à empresa selecionada
    contatos = list(collection_contatos.find({"empresa": empresa_cnpj}, {"_id": 0}))

    with st.expander("📞 Contatos", expanded=True):
        if contatos:
            df_contatos = pd.DataFrame(contatos)

            df_contatos = df_contatos.rename(
                columns={
                    "nome": "Nome",
                    "sobrenome": "Sobrenome",
                    "cargo": "Cargo",
                    "email": "E-mail",
                    "fone": "Telefone"
                }
            )

            df_contatos = df_contatos[["Nome", "Sobrenome", "Cargo", "E-mail", "Telefone"]]

            st.dataframe(df_contatos, hide_index=True, use_container_width=True)
        else:
            st.warning("Nenhum contato cadastrado para esta empresa.")

        # Verifica permissão para adicionar, editar ou remover contatos
        if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):

            with st.popover('➕ Adicionar Contato'):
                with st.form("form_adicionar_contato"):
                    st.subheader("➕ Adicionar Contato")
                    nome = st.text_input("Nome *")
                    sobrenome = st.text_input("Sobrenome")
                    cargo = st.text_input("Cargo")
                    email = st.text_input("E-mail *")
                    telefone = st.text_input("Telefone")

                    submit_adicionar = st.form_submit_button("✅ Adicionar Contato")

                    if submit_adicionar:
                        if nome and email:
                            collection_contatos.insert_one({
                                "nome": nome,
                                "sobrenome": sobrenome,
                                "cargo": cargo,
                                "email": email,
                                "fone": telefone,
                                "empresa": empresa_cnpj  # Garantir que o contato seja vinculado à empresa selecionada
                            })
                            st.success("Contato adicionado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Preencha os campos obrigatórios: Nome e E-mail.")

            # Se houver contatos cadastrados, exibir opções de edição/remoção
            if contatos:
                with st.popover('✏️ Editar contato'):
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

                                submit_editar = st.form_submit_button("💾 Salvar Alterações")
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
