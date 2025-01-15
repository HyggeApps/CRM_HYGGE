import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from google.oauth2.service_account import Credentials
from firebase_admin import initialize_app
import streamlit_authenticator as stauth

# Configurações do Firebase
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

# Função para adicionar novo usuário
def add_user(user_data):
    ref = db.reference('users')
    ref.push(user_data)
    st.success("Usuário cadastrado com sucesso!")

# Função para cadastrar novo usuário
def register_user():
    st.subheader("Cadastrar Novo Usuário")
    nome = st.text_input("Nome")
    sobrenome = st.text_input("Sobrenome")
    email = st.text_input("Email")
    fone = st.text_input("Fone")
    setor = st.text_input("Setor")
    login = st.text_input("Login")
    senha = st.text_input("Senha", type="password")
    hierarquia = st.selectbox("Hierarquia", ["Administrador", "Gerente", "Funcionário"])

    if st.button("Cadastrar"):
        if nome and sobrenome and email and fone and setor and login and senha:
            user_data = {
                "Nome": nome,
                "Sobrenome": sobrenome,
                "Email": email,
                "Fone": fone,
                "Setor": setor,
                "Login": login,
                "Senha": senha,  # Note: Consider hashing the password in a real app
                "Hierarquia": hierarquia
            }
            add_user(user_data)
        else:
            st.error("Por favor, preencha todos os campos.")

# Função de autenticação (login)
def authenticate_user():
    users = fetch_users()
    
    usernames = [user_data['Login'] for user_data in users.values()]
    passwords = [user_data['Senha'] for user_data in users.values()]

    authenticator = stauth.Authenticate(
        usernames, passwords, "crm_hygge", "cookie", cookie_expiry_days=30
    )

    name, authentication_status = authenticator.login("Login", "main")

    if authentication_status:
        st.write(f"Bem-vindo, {name}!")
    else:
        if authentication_status == False:
            st.error("Nome de usuário ou senha incorretos.")
        elif authentication_status == None:
            st.warning("Por favor, insira suas credenciais.")

# Opções do menu
menu = ["Login", "Cadastrar Novo Usuário"]
choice = st.sidebar.selectbox("Escolha uma opção", menu)

if choice == "Login":
    authenticate_user()
elif choice == "Cadastrar Novo Usuário":
    register_user()
