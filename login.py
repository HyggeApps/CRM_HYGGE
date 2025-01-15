import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Defina a variável de ambiente explicitamente
os.environ["GOOGLE_CLOUD_PROJECT"] = "crm-hygge"

# Inicializar o Firebase
def init_firebase():
    if not firebase_admin._apps:  # Evitar inicializações múltiplas
        cred = credentials.Certificate("crm-hygge-firebase-adminsdk-idxya-52f8b98280.json")
        firebase_admin.initialize_app(cred, {
            'projectId': 'crm-hygge'  # Substitua pelo seu Project ID
        })

init_firebase()

# Função para obter dados do Firestore
def get_firestore_data(collection_name):
    try:
        db = firestore.client()
        docs = db.collection(collection_name).stream()
        data = [{doc.id: doc.to_dict()} for doc in docs]
        return data
    except Exception as e:
        st.error(f"Erro ao acessar o Firestore: {e}")
        return []

# Interface do Streamlit
st.title("Dados do Firestore")

collection_name = st.text_input("Nome da Coleção", "users")  # Coleção padrão: "users"
if st.button("Exibir Dados"):
    data = get_firestore_data(collection_name)
    if data:
        st.write(f"Dados na coleção '{collection_name}':")
        for doc in data:
            st.json(doc)
    else:
        st.warning("Nenhum dado encontrado ou erro na consulta.")
