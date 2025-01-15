import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Obter as credenciais do Streamlit Secrets
firebase_credentials_str = st.secrets["firebase"]

# Converter a string de credenciais para um dicionário
firebase_credentials = json.loads(json.dumps(firebase_credentials_str))

# Inicializar o Firebase
cred = credentials.Certificate(firebase_credentials)
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
