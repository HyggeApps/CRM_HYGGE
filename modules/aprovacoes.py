import streamlit as st
from utils.database import get_collection
import datetime as dt

@st.fragment
def gerenciamento_aprovacoes():
    # Obter as coleções
    col_oportunidades = get_collection("oportunidades")
    col_aprovacoes = get_collection("aprovacoes")
    
    # Buscar oportunidades com solicitação de desconto
    oportunidades = list(col_oportunidades.find({"solicitacao_desconto": True}))
    
    if not oportunidades:
        st.info("Não há oportunidades com solicitação de desconto.")
        return

    st.header("Oportunidades com Solicitação de Desconto")
    
    # Exibir cada oportunidade em uma linha
    for oportunidade in oportunidades:
        # Cria 5 colunas para exibir as informações e o botão de aprovação
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.text_input(
                label="Empresa", 
                value=oportunidade.get("cliente", "N/A"), 
                disabled=True
            )
        with col2:
            st.text_input(
                label="Negócio", 
                value=oportunidade.get("nome_oportunidade", "N/A"), 
                disabled=True
            )
        with col3:
            st.text_input(
                label="Vendedor", 
                value=oportunidade.get("proprietario", "N/A"), 
                disabled=True
            )
        with col4:
            st.text_input(
                label="Desconto Solicitado", 
                value=str(oportunidade.get("desconto_aprovado", "N/A")), 
                disabled=True
            )
        with col5:
            st.text('')
            st.text('')
            if st.button("Aprovar Desconto", key=str(oportunidade["_id"]),use_container_width=True):
                # Atualiza o campo aprovacao_gestor na oportunidade
                col_oportunidades.update_one(
                    {"_id": oportunidade["_id"]},
                    {"$set": {"aprovacao_gestor": True}}
                )
                
                # Cria um registro na coleção 'aprovacoes'
                aprovacao = {
                    "oportunidade_id": oportunidade["_id"],
                    "empresa": oportunidade.get("cliente", "N/A"),
                    "nome_oportunidade": oportunidade.get("nome_oportunidade", "N/A"),
                    "vendedor": oportunidade.get("proprietario", "N/A"),
                    "desconto_solicitado": oportunidade.get("desconto_aprovado", "N/A"),
                    "aprovado_por": "gestor",  # Substitua pela identificação do usuário logado, se necessário
                    "data_aprovacao": dt.datetime.now()
                }
                col_aprovacoes.insert_one(aprovacao)
                st.success("Desconto aprovado com sucesso!")
