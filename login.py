import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

# Defina a variável de ambiente explicitamente
os.environ["GOOGLE_CLOUD_PROJECT"] = "crm-hygge"

# Inicializar o Firebase
def init_firebase():
    if not firebase_admin._apps:  # Evitar inicializações múltiplas
        cred = credentials.Certificate("crm-hygge-firebase-adminsdk-idxya-52f8b98280.json")
        firebase_admin.initialize_app(cred)

# Inicializar Firebase
init_firebase()

# Adicionar usuário ao Firestore
def add_user_to_firestore(username, name, password):
    db = firestore.client()
    # Criar hash da senha corretamente
    hasher = stauth.Hasher([password])  # Instanciar o hasher com a senha
    hashed_password = hasher.generate()[0]  # Gerar o hash da senha
    db.collection("users").document(username).set({
        "username": username,
        "name": name,
        "password": hashed_password
    })

# Exemplo de adição de usuário
add_user_to_firestore("user3", "User Three", "password123")