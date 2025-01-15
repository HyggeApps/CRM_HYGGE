import streamlit as st
from utils.database import get_collection

def cadastro_produtos():
    st.title("Cadastro de Produtos")
    collection = get_collection("produtos")

    with st.form("produto_form"):
        nome_produto = st.text_input("Nome do Produto", "")
        categoria = st.text_input("Categoria", "")
        preco = st.number_input("Preço", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Cadastrar")

        if submit:
            if nome_produto:
                document = {"nome_produto": nome_produto, "categoria": categoria, "preco": preco}
                collection.insert_one(document)
                st.success("Produto cadastrado com sucesso!")
            else:
                st.error("Preencha o nome do produto.")