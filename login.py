import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, db

firebase_credentials = st.secrets["firebase"]

# Inicializando o Firebase
def init_firebase(fb_cred):
    if not firebase_admin._apps:
        # Carregue sua chave privada do Firebase
        cred = credentials.Certificate(fb_cred)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://<your-database-name>.firebaseio.com'  # Insira o URL do seu banco de dados
        })

# Funções auxiliares para acessar o banco de dados
def add_data(collection_name, data):
    db = firestore.client()
    db.collection(collection_name).add(data)

def get_data(collection_name):
    db = firestore.client()
    docs = db.collection(collection_name).stream()
    return [{doc.id: doc.to_dict()} for doc in docs]

# Interface do Streamlit
st.title("Acesso ao Firebase com Streamlit")

# Inicializando o Firebase
init_firebase(firebase_credentials)

menu = ["Adicionar Dados", "Ver Dados"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Adicionar Dados":
    st.subheader("Adicionar Dados ao Banco")
    collection = st.text_input("Coleção")
    field = st.text_input("Campo")
    value = st.text_input("Valor")

    if st.button("Salvar"):
        if collection and field and value:
            data = {field: value}
            add_data(collection, data)
            st.success("Dados adicionados com sucesso!")
        else:
            st.error("Preencha todos os campos!")

elif choice == "Ver Dados":
    st.subheader("Ver Dados do Banco")
    collection = st.text_input("Coleção para visualizar")
    if st.button("Carregar"):
        if collection:
            data = get_data(collection)
            st.write(data)
        else:
            st.error("Insira o nome da coleção!")