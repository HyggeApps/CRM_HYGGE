import streamlit as st
import pandas as pd
from utils.database import get_collection
import re

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
    contatos = list(collection_contatos.find({}, {"_id": 0}))
    empresas = list(collection_empresas.find(
        {},
        {"_id": 0, "razao_social": 1, "usuario": 1, "ultima_atividade": 1}
    ))

    # Converter para DataFrame
    df_contatos = pd.DataFrame(contatos)
    df_empresas = pd.DataFrame(empresas)

    # Se o DataFrame de contatos não tiver a coluna "empresa", cria-a com "Sem Empresa"
    if "empresa" not in df_contatos.columns:
        df_contatos["empresa"] = "Sem Empresa"
    else:
        df_contatos["empresa"] = df_contatos["empresa"].fillna("Sem Empresa")

    # Renomeia "razao_social" para "Empresa" em empresas para padronizar o merge
    df_empresas.rename(columns={"razao_social": "Empresa"}, inplace=True)

    # Preparar as colunas para merge de forma case-insensitive:
    df_contatos["empresa_lower"] = df_contatos["empresa"].str.lower()
    df_empresas["Empresa_lower"] = df_empresas["Empresa"].str.lower()

    # Merge dos DataFrames com base no nome da empresa (razão social)
    df_merged = df_contatos.merge(
        df_empresas[["Empresa_lower", "usuario", "ultima_atividade"]],
        left_on="empresa_lower",
        right_on="Empresa_lower",
        how="left"
    )

    # Remover colunas auxiliares de merge
    df_merged.drop(columns=["empresa_lower", "Empresa_lower"], inplace=True)

    # Renomear colunas dos contatos para exibição
    df_merged = df_merged.rename(columns={
        "nome": "Nome",
        "sobrenome": "Sobrenome",
        "cargo": "Cargo",
        "email": "E-mail",
        "fone": "Telefone"
    })

    # Organizar a ordem das colunas desejadas.
    # Se o merge não encontrou correspondência, "usuario" e "ultima_atividade" ficarão NaN.
    col_order = ["Nome", "Sobrenome", "empresa", "usuario", "ultima_atividade", "Cargo", "E-mail", "Telefone"]
    col_order = [col for col in col_order if col in df_merged.columns]
    df_final = df_merged[col_order]

    # Campo de busca único
    filtro_busca = st.text_input(
        "🔍 Buscar Contato ou Empresa:",
        placeholder="Digite e pressione Enter",
        key="busca_unica"
    )

    # Aplicar filtro no DataFrame, se houver busca
    if filtro_busca:
        filtro_normalizado = re.sub(r"\s+", " ", filtro_busca.strip().lower())
        df_final["busca_concat"] = (
            df_final["Nome"].fillna("") + " " +
            df_final["Sobrenome"].fillna("") + " " +
            df_final["empresa"].fillna("")
        ).str.lower().apply(lambda x: re.sub(r"\s+", " ", x))
        df_final = df_final[df_final["busca_concat"].str.contains(filtro_normalizado, na=False)]
    
    if "busca_concat" in df_final.columns:
        df_final.drop(columns=["busca_concat"], inplace=True)

    # Exibir DataFrame com data_editor
    st.data_editor(df_final, hide_index=True, use_container_width=True)

