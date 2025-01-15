import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
from google.oauth2.service_account import Credentials
from firebase_admin import initialize_app

firebase_credentials = st.secrets["firebase"]

if not firebase_admin._apps:
    cred = Credentials.from_service_account_info(firebase_credentials)
    initialize_app(cred, {
        'databaseURL': 'https://crm-hygge-default-rtdb.firebaseio.com/'
    })
    
# Função para acessar os usuários
def fetch_users():
    ref = db.reference('users')
    return ref.get() or {}

try:
    users = fetch_users()
    st.write("Usuários no banco de dados:", users)
except Exception as e:
    st.error(f"Erro ao acessar o banco de dados: {e}")
    st.write("Detalhes do erro:", str(e))
