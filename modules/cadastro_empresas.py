import streamlit as st
from utils.database import get_collection

def cadastro_empresas():
    st.title("Cadastro de Empresas")
    collection = get_collection("empresas")

    with st.form("empresa_form"):
        nome_empresa = st.text_input("Nome da Empresa", "")
        cnpj = st.text_input("CNPJ", "")
        setor = st.text_input("Setor", "")
        submit = st.form_submit_button("Cadastrar")

        if submit:
            if nome_empresa and cnpj:
                existing_company = collection.find_one({"cnpj": cnpj})
                if existing_company:
                    st.error("Empresa já cadastrada com este CNPJ!")
                else:
                    document = {"nome_empresa": nome_empresa, "cnpj": cnpj, "setor": setor}
                    collection.insert_one(document)
                    st.success("Empresa cadastrada com sucesso!")
            else:
                st.error("Preencha os campos obrigatórios.")
