import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Obter credenciais do secrets do Streamlit
firebase_credentials = st.secrets["firebase"]

# Inicializar o Firebase
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://crm-hygge-default-rtdb.firebaseio.com/'
})

# Funções para manipular usuários no banco de dados
def fetch_users():
    ref = db.reference('users')
    return ref.get() or {}

def save_user(username, email, name, password):
    ref = db.reference(f'users/{username}')
    ref.set({
        'email': email,
        'name': name,
        'password': password,
    })

# Teste inicial
try:
    users = fetch_users()
    st.write("Usuários no banco:", users)
except Exception as e:
    st.error(f"Erro ao conectar com o Firebase: {e}")