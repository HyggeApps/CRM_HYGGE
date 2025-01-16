import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import streamlit as st
from modules import (
    cadastro_usuarios,
    cadastro_empresas,
    cadastro_produtos,
    cadastro_oportunidades,
    cadastro_templates,
    cadastro_contatos,
    cadastro_orcamentos,
    cadastro_subempresas,
    cadastro_leads,
)
from utils import functions as funcs
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
import json

# Configuração da página
st.set_page_config(
    page_title='HYGGE - Ambiente de certificação ambiental', layout='wide',
    page_icon='https://hygge.eco.br/wp-content/uploads/2022/06/Logo_site.png'
)

image1 = 'https://hygge.eco.br/wp-content/uploads/2024/07/white.png'
image_width_percent = 40

html_code1 = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100%; ">
        <img src="{image1}" alt="Image" style="width: {image_width_percent}%;"/>
    </div>
"""
st.sidebar.markdown(html_code1, unsafe_allow_html=True)

custom_css = """
    <style>
    .main {
        max-width: 80%;
        margin: 0 auto;
    }
    section[data-testid="stSidebar"] {
        width: 400px !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.sidebar.markdown('------')

# Criar um arquivo temporário com os usuários do MongoDB
#temp_config_path = funcs.create_temp_config_from_mongo(mongo_uri, db_name, collection_name)

# Carregar e verificar as chaves no arquivo config.yaml
config_file = "utils\config.yaml"
config_data = funcs.load_config_and_check_or_insert_cookies("utils\config.yaml")

with st.sidebar:
    
    # Loading config file
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=SafeLoader)
        st.write(config)

    # Pre-hashing all plain text passwords once
    # stauth.Hasher.hash_passwords(config['credentials'])

    with st.sidebar:
        # Creating the authenticator object
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )

        # authenticator = stauth.Authenticate(
        #     '../config.yaml'
        # )

        # Creating a login widget
        try:
            authenticator.login()
        except LoginError as e:
            st.error(e)
            
    # Autenticando usuário
    if st.session_state['authentication_status']:
        if 'admin' in st.session_state["roles"]:
            st.info(f'Bem-vindo(a), **{st.session_state["name"]}**!')
            st.info('Este é o ambiente de **admin** para preenchimento das informações referentes ao EVTA de projetos.')
        else:
            st.info(f'Bem-vindo(a), **{st.session_state["name"]}**!')
            st.info('Este é o ambiente de **usuário** para preenchimento das informações referentes ao EVTA de projetos.')

    elif st.session_state['authentication_status'] is False:
        st.error('Usuário e/ou Senha inválido(s).')
    elif st.session_state['authentication_status'] is None:
        st.warning('Por favor, entre com o seu usuário e senha.')

@st.cache_data
def read_json_creditos(path):
    with open(path, 'r', encoding='utf-8') as file:
        creditos = json.load(file)
        return creditos

@st.cache_data
def read_json_pontuacao_creditos(path):
    with open(path, 'r', encoding='utf-8') as file:
        pontuacao_creditos = json.load(file)
        return pontuacao_creditos

if st.session_state['authentication_status']:
    if 'admin' in st.session_state["roles"]:

        # Título Principal
        st.title("Gerenciador de Cadastros")

        # Configurar as abas
        tabs = st.tabs([
            "Usuários",
            "Empresas (Matriz)",
            "Empresas (Sub-empresas)",
            "Produtos",
            "Templates",
            "Contatos",
            "Leads",
            "Oportunidades",
            "Orçamentos"
        ])

        # Aba: Cadastro de Usuários
        with tabs[0]:
            st.header("Cadastro de Usuários")
            cadastro_usuarios.gerenciamento_usuarios()

        # Aba: Cadastro de Empresas
        with tabs[1]:
            st.header("Cadastro de Empresas (Matriz)")
            cadastro_empresas.gerenciamento_empresas()

        with tabs[2]:
            st.header("Cadastro de Empresas (Sub-empresas)")
            cadastro_subempresas.gerenciamento_subempresas()

        # Aba: Cadastro de Produtos
        with tabs[3]:
            st.header("Cadastro de Produtos")
            cadastro_produtos.gerenciamento_produtos()

        with tabs[4]:
            st.header("Cadastro de Templates")
            cadastro_templates.gerenciamento_templates()

        with tabs[5]:
            st.header("Cadastro de Contatos")
            cadastro_contatos.gerenciamento_contatos()

        with tabs[6]:
            st.header("Cadastro de Leads")
            cadastro_leads.gerenciamento_leads()

        with tabs[7]:
            st.header("Cadastro de Oportunidades")
            cadastro_oportunidades.gerenciamento_oportunidades()

        with tabs[8]:
            st.header("Cadastro de Orçamento")
            cadastro_orcamentos.gerenciamento_orcamentos()