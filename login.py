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
        firebase_admin.initialize_app(cred)

# Inicializar Firebase
init_firebase()

# Função para listar dados do Firestore
def list_firestore_data(collection_name):
    try:
        db = firestore.client()
        docs = db.collection(collection_name).stream()
        data = [{doc.id: doc.to_dict()} for doc in docs]
        return data
    except Exception as e:
        st.error(f"Erro ao acessar o Firestore: {e}")
        return []

# Interface do Streamlit
st.title("Listar Conteúdo do Firestore")

# Entrada para o nome da coleção
collection_name = st.text_input("Digite o nome da coleção:", "users")

# Botão para listar dados
if st.button("Listar Dados"):
    st.write(f"Listando documentos da coleção: {collection_name}")
    data = list_firestore_data(collection_name)
    if data:
        for index, doc in enumerate(data):
            st.write(f"Documento {index + 1}:")
            st.json(doc)
    else:
        st.warning("Nenhum documento encontrado na coleção ou a coleção não existe.")
