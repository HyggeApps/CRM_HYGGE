import streamlit as st
from utils.database import get_collection
import streamlit_authenticator as stauth
from pymongo import MongoClient

def configurar_login():
    # Conectar à coleção de usuários
    collection_usuarios = get_collection("usuarios")
    
    # Obter usuários cadastrados
    usuarios = list(collection_usuarios.find({}, {"_id": 0, "login": 1, "senha": 1, "nome": 1, "sobrenome": 1}))

    if not usuarios:
        st.warning("Nenhum usuário encontrado no banco de dados. Cadastre usuários para habilitar o login.")
        return

    # Construir dicionário de credenciais
    credentials = {
        "usernames": {
            usuario["login"]: {
                "name": f"{usuario['nome']} {usuario['sobrenome']}",
                "password": usuario["senha"],  # A senha deve estar previamente hasheada
            }
            for usuario in usuarios
        }
    }

    # Configurar autenticação
    authenticator = stauth.Authenticate(
        credentials,
        "crm_hygge",  # Nome do app
        "auth_cookie",  # Nome do cookie
        cookie_expiry_days=30,
    )

    # Login
    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        st.success(f"Bem-vindo, {name}!")
        authenticator.logout("Sair", "sidebar")
    elif authentication_status is False:
        st.error("Usuário ou senha incorretos.")
    elif authentication_status is None:
        st.warning("Por favor, insira suas credenciais.")
