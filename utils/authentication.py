import streamlit as st
import streamlit_authenticator as stauth
from utils.database import get_collection

def configurar_login():
    collection_usuarios = get_collection("usuarios")

    usuarios = list(collection_usuarios.find({}, {"_id": 0, "login": 1, "senha": 1, "nome": 1, "sobrenome": 1}))

    if not usuarios:
        st.warning("Nenhum usuário encontrado. Por favor, cadastre usuários no banco de dados.")
        return None, None, None

    credentials = {
        "usernames": {
            usuario["login"]: {
                "name": f"{usuario['nome']} {usuario['sobrenome']}",
                "password": usuario["senha"],  # As senhas devem estar previamente hasheadas
            }
            for usuario in usuarios
        }
    }

    authenticator = stauth.Authenticate(
        credentials,
        "crm_hygge",  # Nome do app
        "auth_cookie",  # Nome do cookie
        cookie_expiry_days=30,
    )

    # Certifique-se de passar "main", "sidebar" ou "unrendered"
    return authenticator.login("Login", "sidebar")  # Corrigido para "sidebar"