import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, db

firebase_credentials = st.secrets["firebase"]

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar o Firebase
def init_firebase():
    if not firebase_admin._apps:  # Evitar inicialização duplicada
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)

# Funções auxiliares para manipular o Firestore
def add_data(collection_name, data):
    db = firestore.client()
    db.collection(collection_name).add(data)

def get_data(collection_name):
    db = firestore.client()
    docs = db.collection(collection_name).stream()
    return [{doc.id: doc.to_dict()} for doc in docs]

# Inicializar Firebase
init_firebase()

# Interface do Streamlit
st.title("Gerenciador de Dados com Firestore")

menu = ["Adicionar Dados", "Ver Dados"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Adicionar Dados":
    st.subheader("Adicionar Dados")
    collection = st.text_input("Nome da Coleção")
    field = st.text_input("Campo")
    value = st.text_input("Valor")
    
    if st.button("Salvar"):
        if collection and field and value:
            data = {field: value}
            add_data(collection, data)
            st.success(f"Dado adicionado à coleção '{collection}'!")
        else:
            st.error("Por favor, preencha todos os campos.")

elif choice == "Ver Dados":
    st.subheader("Ver Dados")
    collection = st.text_input("Coleção para visualizar")
    
    if st.button("Carregar"):
        if collection:
            data = get_data(collection)
            st.write(data)
        else:
            st.error("Insira o nome da coleção!")
