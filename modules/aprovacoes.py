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
    
    # Exibir cada oportunidade em uma linha com colunas e Markdown
    for oportunidade in oportunidades:
        cols = st.columns(5)
        cols[0].markdown(f"**Empresa:** {oportunidade.get('cliente', 'N/A')}")
        cols[1].markdown(f"**Negócio:** {oportunidade.get('nome_oportunidade', 'N/A')}")
        cols[2].markdown(f"**Vendedor:** {oportunidade.get('proprietario', 'N/A')}")
        cols[3].markdown(f"**Desconto Solicitado:** {oportunidade.get('desconto_aprovado', 'N/A')}")
        
        if cols[4].button("Aprovar Desconto", key=str(oportunidade["_id"])):
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
                "aprovado_por": "gestor",  # Personalize conforme o usuário logado
                "data_aprovacao": dt.datetime.now()
            }
            col_aprovacoes.insert_one(aprovacao)
            st.success("Desconto aprovado com sucesso!")
