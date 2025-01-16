import streamlit as st
import streamlit_authenticator as stauth
from utils.database import get_collection

def configurar_login():
    # Buscar usuários do banco de dados
    collection_usuarios = get_collection("usuarios")
    usuarios = list(collection_usuarios.find({}, {"_id": 0, "login": 1, "senha": 1, "nome": 1, "sobrenome": 1}))

    if not usuarios:
        st.warning("Nenhum usuário encontrado. Por favor, cadastre usuários no banco de dados.")
        return None, None, None

    # Construir credenciais
    credentials = {
        "usernames": {
            usuario["login"]: {
                "name": f"{usuario['nome']} {usuario['sobrenome']}",
                "password": usuario["senha"],  # As senhas devem estar hasheadas
            }
            for usuario in usuarios
        }
    }

    # Configuração do Authenticator
    authenticator = stauth.Authenticate(
        credentials,
        "crm_hygge",
        "auth_cookie",
        cookie_expiry_days=30,
    )

    # Usar "unrendered" para renderizar manualmente
    name, authentication_status, username = authenticator.login("Login", "unrendered")

    if authentication_status is None:
        st.warning("Por favor, insira suas credenciais abaixo.")
        authenticator._login_block()  # Renderiza manualmente o formulário de login

    return name, authentication_status, username
