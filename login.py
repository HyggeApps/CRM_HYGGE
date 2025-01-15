import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar o Firebase
def init_firebase():
    if not firebase_admin._apps:  # Evitar inicializações múltiplas
        cred = credentials.Certificate("crm-hygge-firebase-adminsdk-idxya-52f8b98280.json")
        firebase_admin.initialize_app(cred, {
            'projectId': 'crm-hygge'  # Substitua pelo seu Project ID
        })

# Inicializar o Firebase
init_firebase()

# Testar conexão
try:
    db = firestore.client()
    st.success("Conexão com o Firestore realizada com sucesso!")
except Exception as e:
    st.error(f"Erro ao conectar com o Firestore: {e}")
