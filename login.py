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

# Conectar ao Firestore
db = firestore.client()

# Função para adicionar dados
def add_to_firestore(collection_name, document_data):
    try:
        db.collection(collection_name).add(document_data)
        st.success("Documento adicionado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao adicionar documento: {e}")

# Função para listar dados
def read_from_firestore(collection_name):
    try:
        docs = db.collection(collection_name).stream()
        data = [{doc.id: doc.to_dict()} for doc in docs]
        return data
    except Exception as e:
        st.error(f"Erro ao ler documentos: {e}")
        return []

# Interface do Streamlit
st.title("Firestore: Escrita e Leitura")

# Adicionar dados
st.header("Adicionar Documento")
collection_name = st.text_input("Nome da coleção:", "test_collection")
field = st.text_input("Campo:")
value = st.text_input("Valor:")
if st.button("Adicionar"):
    if collection_name and field and value:
        add_to_firestore(collection_name, {field: value})
    else:
        st.error("Por favor, preencha todos os campos.")

# Ler dados
st.header("Ler Documentos")
if st.button("Listar Dados"):
    if collection_name:
        data = read_from_firestore(collection_name)
        if data:
            st.write(f"Documentos na coleção '{collection_name}':")
            for index, doc in enumerate(data):
                st.write(f"Documento {index + 1}:")
                st.json(doc)
        else:
            st.warning(f"Nenhum documento encontrado na coleção '{collection_name}'.")
    else:
        st.error("Por favor, insira o nome da coleção.")
