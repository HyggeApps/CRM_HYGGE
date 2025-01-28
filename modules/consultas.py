import streamlit as st
from utils.database import get_collection

def consultar_empresas():
    collection_empresas = get_collection("empresas")
    st.header("Empresas cadastradas na base de dados da HYGGE")
    st.info("Visualize e filtre as empresas cadastradas na nossa base de dados.")
    st.write('----')

    # Obter lista de vendedores
    vendedores = list(collection_empresas.distinct("usuario"))
    vendedores = [v for v in vendedores if v]

    # Filtros
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        filtro_razao_social = st.text_input("Razão Social", placeholder="Parte da Razão Social")
    with col2:
        filtro_cnpj = st.text_input("CNPJ", placeholder="Parte do CNPJ")
    with col3:
        filtro_cidade = st.text_input("Cidade", placeholder="Digite a cidade")
    with col4:
        filtro_estado = st.text_input("Estado (UF)", max_chars=2, placeholder="Ex: SP")
    with col5:
        filtro_tamanho = st.multiselect(
            "Tamanho",
            options=["Pequena", "Média", "Grande"],
            default=[],
        )
    with col6:
        filtro_vendedor = st.selectbox(
            "Vendedor",
            options=["Todos"] + vendedores,
            index=0,
        )

    # Construir query de filtro
    query = {}
    if filtro_razao_social:
        query["razao_social"] = {"$regex": filtro_razao_social, "$options": "i"}
    if filtro_cnpj:
        query["cnpj"] = {"$regex": filtro_cnpj, "$options": "i"}
    if filtro_cidade:
        query["cidade"] = {"$regex": filtro_cidade, "$options": "i"}
    if filtro_estado:
        query["estado"] = filtro_estado.upper()
    if filtro_tamanho:
        query["tamanho_empresa"] = {"$in": filtro_tamanho}
    if filtro_vendedor and filtro_vendedor != "Todos":
        query["usuario"] = filtro_vendedor

    # Buscar empresas no banco de dados com os filtros aplicados
    empresas_filtradas = list(
        collection_empresas.find(
            query,
            {
                "_id": 0,
                "razao_social": 1,
                "cnpj": 1,
                "cidade": 1,
                "estado": 1,
                "pais": 1,
                "tamanho_empresa": 1,
                "usuario": 1,
            },
        )
    )

    # Exibir tabela ou mensagem de alerta
    if empresas_filtradas:
        import pandas as pd

        df_empresas = pd.DataFrame(empresas_filtradas)
        df_empresas = df_empresas.rename(
            columns={
                "razao_social": "Razão Social",
                "cnpj": "CNPJ",
                "cidade": "Cidade",
                "estado": "UF",
                "pais": "País",
                "tamanho_empresa": "Tamanho",
                "usuario": "Vendedor",
            }
        )
        st.dataframe(df_empresas, use_container_width=True)
    else:
        st.warning("Nenhuma empresa encontrada com os critérios aplicados.")