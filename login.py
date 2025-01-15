import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Obter as credenciais do Streamlit Secrets
firebase_credentials = st.secrets["firebase"]

# Inicializar o Firebase usando o objeto diretamente
cred = credentials.Certificate(dict(firebase_credentials))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://crm-hygge-default-rtdb.firebaseio.com/'
})

# Função para testar a conexão
def fetch_users():
    ref = db.reference('users')
    return ref.get() or {}

# Testar o acesso
try:
    users = fetch_users()
    st.write("Usuários no banco de dados:", users)
except Exception as e:
    st.error(f"Erro ao acessar o Firebase: {e}")
