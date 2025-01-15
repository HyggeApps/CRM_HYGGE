import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz

firebase_credentials = st.secrets["firebase"]

st.write(firebase_credentials)

# Verificar se o Firebase já está inicializado
if not firebase_admin._apps:
    # Inicializar o Firebase
    cred = credentials.Certificate(dict(firebase_credentials))
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://crm-hygge-default-rtdb.firebaseio.com/'
    })

# Função para acessar os usuários
def fetch_users():
    ref = db.reference('users')
    return ref.get() or {}

# Testar a conexão
try:
    users = fetch_users()
    st.write("Usuários no banco de dados:", users)
except Exception as e:
    st.error(f"Erro ao acessar o banco de dados: {e}")
