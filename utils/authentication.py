import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import streamlit as st

def load_config(config_path='utils/config.yaml'):
    """Carregar as configurações do arquivo YAML."""
    try:
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo de configuração: {e}")
        return None

def configurar_login():
    """Configurar o sistema de autenticação."""
    # Carregar configurações
    config = load_config()
    if not config:
        return None, None, None

    # Inicializar o autenticador
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        preauthorized=config.get('preauthorized')
    )

    # Login
    name, authentication_status, username = authenticator.login('Login', location='main')

    # Logout configurado para exibir na barra lateral
    if authentication_status:
        authenticator.logout('Sair', 'sidebar')

    return name, authentication_status, username