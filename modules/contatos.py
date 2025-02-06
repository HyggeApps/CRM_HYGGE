import streamlit as st
import pandas as pd
from utils.database import get_collection
import time

@st.fragment
def exibir_contatos_empresa(user, admin, empresa_cnpj):
    collection_contatos = get_collection("contatos")

    # Buscar **apenas** os contatos vinculados à empresa atualmente selecionada
    contatos = list(collection_contatos.find({"empresa": empresa_cnpj}, {"_id": 0}))

    # Verifica permissão para adicionar, editar ou remover contatos
    if admin or (user == st.session_state["empresa_selecionada"]["Proprietário"]):

        with st.popover('➕ Adicionar Contato'):
            with st.form("form_adicionar_contato"):
                st.subheader("➕ Adicionar Contato")
                
                # Criar duas colunas para organização do formulário
                col1, col2 = st.columns(2)

                with col1:
                    nome = st.text_input("Nome *")
                    cargo = st.text_input("Cargo")
                    telefone = st.text_input("Telefone")

                with col2:
                    sobrenome = st.text_input("Sobrenome")
                    email = st.text_input("E-mail *")

                submit_adicionar = st.form_submit_button("✅ Adicionar Contato")

                if submit_adicionar:
                    # Verificar se o contato já existe em **outra empresa**
                    contato_existente = collection_contatos.find_one({"email": email})
                    if contato_existente and contato_existente["empresa"] != empresa_cnpj:
                        st.error(f"Erro: O contato '{email}' já está vinculado à empresa de CNPJ {contato_existente['empresa']}!")
                    else:
                        # Adicionar contato APENAS à empresa selecionada
                        collection_contatos.insert_one({
                            "nome": nome,
                            "sobrenome": sobrenome,
                            "cargo": cargo,
                            "email": email,
                            "fone": telefone,
                            "empresa": empresa_cnpj  # O contato pertence APENAS a essa empresa!
                        })
                        
                        st.success("Contato adicionado com sucesso!")
                        st.rerun()
                        
                        
                        

        # Se houver contatos cadastrados, exibir opções de edição/remoção
        if contatos:
            with st.popover('✏️ Editar contato'):
                contato_selecionado = st.selectbox(
                    "Selecione um contato para editar/remover",
                    options=[f"{c['nome']} {c['sobrenome']} ({c['email']})" for c in contatos]
                )

                if contato_selecionado:
                    email_editar = contato_selecionado.split("(")[-1].strip(")")

                    contato_dados = collection_contatos.find_one({"email": email_editar, "empresa": empresa_cnpj}, {"_id": 0})

                    if contato_dados:
                        with st.form("form_editar_contato"):
                            st.subheader("✏️ Editar Contato")

                            # Criar duas colunas para melhor organização dos campos
                            col1, col2 = st.columns(2)

                            with col1:
                                nome_edit = st.text_input("Nome", value=contato_dados.get("nome", ""))
                                cargo_edit = st.text_input("Cargo", value=contato_dados.get("cargo", ""))
                                telefone_edit = st.text_input("Telefone", value=contato_dados.get("fone", ""))

                            with col2:
                                sobrenome_edit = st.text_input("Sobrenome", value=contato_dados.get("sobrenome", ""))
                                email_edit = st.text_input("E-mail", value=contato_dados.get("email", ""), disabled=True)

                            submit_editar = st.form_submit_button("💾 Salvar Alterações")

                            if submit_editar:
                                collection_contatos.update_one(
                                    {"email": email_editar, "empresa": empresa_cnpj},  # Apenas para a empresa correta
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
                        collection_contatos.delete_one({"email": email_editar, "empresa": empresa_cnpj})  # Apenas na empresa vinculada
                        st.success(f"Contato {contato_selecionado} removido com sucesso!")
                        st.rerun()
                        
                        
                        
                        
    contatos = list(collection_contatos.find({"empresa": empresa_cnpj}, {"_id": 0}))
    with st.expander("📞 Contatos cadastrados", expanded=True):
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

        
@st.fragment
def exibir_todos_contatos_empresa():
    # Carregar coleções
    collection_contatos = get_collection("contatos")
    collection_empresas = get_collection("empresas")

    # Buscar dados
    contatos = list(collection_contatos.find({}, {"_id": 0}))  # Exclui o _id para facilitar visualização
    empresas = list(collection_empresas.find({}, {"_id": 0, "nome": 1, "cnpj": 1}))  # Pega apenas nome e CNPJ

    # Converter para DataFrame
    df_contatos = pd.DataFrame(contatos)
    df_empresas = pd.DataFrame(empresas)

    # Renomear CNPJ para corresponder
    df_empresas.rename(columns={"cnpj": "empresa", "nome": "Empresa"}, inplace=True)

    # Mesclar os dados para obter nome da empresa
    df_contatos = df_contatos.merge(df_empresas, on="empresa", how="left")

    # Renomear colunas e organizar ordem
    df_contatos = df_contatos.rename(
        columns={
            "nome": "Nome",
            "sobrenome": "Sobrenome",
            "cargo": "Cargo",
            "email": "E-mail",
            "fone": "Telefone"
        }
    )

    df_contatos = df_contatos[["Nome", "Sobrenome", "Cargo", "E-mail", "Telefone", "Empresa"]]

    # Streamlit UI
    st.title("📇 Lista de Contatos")

    # Filtro por empresa
    empresas_unicas = df_contatos["Empresa"].dropna().unique()
    empresa_selecionada = st.selectbox("Selecione a empresa:", ["Todas"] + list(empresas_unicas))

    # Filtrar os dados
    if empresa_selecionada != "Todas":
        df_contatos = df_contatos[df_contatos["Empresa"] == empresa_selecionada]

    # Exibir DataFrame no Streamlit
    st.dataframe(df_contatos, hide_index=True, use_container_width=True)