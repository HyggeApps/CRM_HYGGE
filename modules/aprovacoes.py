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
    
    # Para cada oportunidade, exibir informações e botão de aprovação
    for oportunidade in oportunidades:
        st.subheader(f"Oportunidade: {oportunidade.get('nome_oportunidade', 'N/A')}")
        st.write("**Empresa:**", oportunidade.get("cliente", "N/A"))
        st.write("**Vendedor:**", oportunidade.get("proprietario", "N/A"))
        st.write("**Desconto Solicitado:**", oportunidade.get("desconto_aprovado", "N/A"))
        
        # Botão para aprovar o desconto
        if st.button("Aprovar Desconto", key=str(oportunidade["_id"])):
            # Atualiza o campo aprovacao_gestor para True na coleção de oportunidades
            col_oportunidades.update_one(
                {"_id": oportunidade["_id"]},
                {"$set": {"aprovacao_gestor": True}}
            )
            
            # Cria um registro de aprovação na coleção 'aprovacoes'
            aprovacao = {
                "oportunidade_id": oportunidade["_id"],
                "empresa": oportunidade.get("cliente", "N/A"),
                "nome_oportunidade": oportunidade.get("nome_oportunidade", "N/A"),
                "vendedor": oportunidade.get("proprietario", "N/A"),
                "desconto_solicitado": oportunidade.get("desconto_aprovado", "N/A"),
                "aprovado_por": "gestor",  # Aqui você pode personalizar para pegar o usuário logado, por exemplo
                "data_aprovacao": dt.datetime.now()
            }
            col_aprovacoes.insert_one(aprovacao)
            st.success("Desconto aprovado com sucesso!")
