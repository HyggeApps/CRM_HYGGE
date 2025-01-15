import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Obter credenciais do Streamlit Secrets
firebase_credentials = st.secrets["firebase"]

# Verificar se o Firebase já está inicializado
if not firebase_admin._apps:
    # Inicializar o Firebase
    cred = credentials.Certificate(dict(firebase_credentials))
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://crm-hygge-default-rtdb.firebaseio.com/'
    })

# Função para exibir todo o banco de dados
def fetch_database():
    try:
        ref = db.reference('/')  # Referência raiz do banco de dados
        data = ref.get()  # Obter todos os dados
        if data:
            st.write("Dados do banco de dados:", data)
        else:
            st.write("O banco de dados está vazio.")
    except Exception as e:
        st.error(f"Erro ao acessar o banco de dados: {e}")

# Exibir dados no Streamlit
st.title("Visualizar Banco de Dados Firebase")
st.button("Carregar Banco de Dados", on_click=fetch_database)
