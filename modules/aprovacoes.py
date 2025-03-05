import streamlit as st
from utils.database import get_collection
import pandas as pd
import datetime as dt
from bson import ObjectId

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
    
    # Criar um DataFrame a partir das oportunidades e converter _id para string
    df = pd.DataFrame(oportunidades)
    df['_id'] = df['_id'].astype(str)
    
    # Selecionar as colunas que serão exibidas
    df_display = df[['_id', 'cliente', 'nome_oportunidade', 'proprietario', 'desconto_aprovado', 'aprovacao_gestor']]
    
    st.write("### Oportunidades com Solicitação de Desconto")
    st.markdown("**Legenda:**  *cliente* = Empresa, *nome_oportunidade* = Negócio, *proprietario* = Vendedor, *desconto_aprovado* = Desconto Solicitado")
    
    # Exibir o DataFrame com st.data_editor (permitindo edição do campo de aprovação)
    edited_df = st.data_editor(df_display, num_rows="dynamic")
    
    # Botão para salvar as alterações (aprovações)
    if st.button("Salvar Aprovações"):
        # Iterar pelas linhas do DataFrame editado
        for idx, row in edited_df.iterrows():
            # Comparar com o status original para identificar alteração (apenas aprova se antes estava False)
            original_status = df_display.loc[df_display['_id'] == row['_id'], 'aprovacao_gestor'].iloc[0]
            if row['aprovacao_gestor'] and not original_status:
                # Atualizar o campo aprovacao_gestor na coleção de oportunidades
                col_oportunidades.update_one(
                    {"_id": ObjectId(row['_id'])},
                    {"$set": {"aprovacao_gestor": True}}
                )
                # Inserir um registro na coleção de aprovacoes
                aprovacao = {
                    "oportunidade_id": row['_id'],
                    "empresa": row['cliente'],
                    "nome_oportunidade": row['nome_oportunidade'],
                    "vendedor": row['proprietario'],
                    "desconto_solicitado": row['desconto_aprovado'],
                    "aprovado_por": "gestor",  # Personalize com o usuário logado, se necessário
                    "data_aprovacao": dt.datetime.now()
                }
                col_aprovacoes.insert_one(aprovacao)
        st.success("Aprovações salvas com sucesso!")