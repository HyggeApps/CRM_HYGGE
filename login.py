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
from utils.database import get_collection

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

# Adicionando CSS personalizado
st.markdown(
    """
    <style>
    /* Ajustar o tamanho da fonte global */
    html, body, [class*="css"] {
        font-size: 0.875rem !important; /* Reduz a fonte em 2pt */
    }

    /* Opcional: Ajustar fontes específicas */
    h1 {
        font-size: 1.75rem !important; /* Tamanho para H1 */
    }
    h2 {
        font-size: 1.5rem !important; /* Tamanho para H2 */
    }
    h3 {
        font-size: 1.25rem !important; /* Tamanho para H3 */
    }
    .stButton > button {
        font-size: 0.875rem !important; /* Botões */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown('------')

# Criar um arquivo temporário com os usuários do MongoDB
collection_usuarios = get_collection("usuarios")
temp_config_path = funcs.create_temp_config_from_mongo(collection_usuarios)
config_data = funcs.load_config_and_check_or_insert_cookies(temp_config_path)

with st.sidebar:
    
    # Loading config file
    with open(temp_config_path, 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=SafeLoader)

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
            st.info('Este é o ambiente de **admin** para consulta, preenchimento e envio das informações referentes as oportunidades.')
        else:
            st.info(f'Bem-vindo(a), **{st.session_state["name"]}**!')
            st.info('Este é o ambiente de **admin** para consulta, preenchimento e envio das informações referentes as oportunidades')

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
        st.title("Gerenciador de oportunidades HYGGE")
        st.write('----')
        #st.info("Neste ambiente você poderá verifique as suas tarefas e indicadores, bem como cadastrar empresas, contatos, oportunidades e orçamentos.")
        st.sidebar.write('')
        hierarquia_atividade = st.sidebar.selectbox('**Selecione o tipo de atividade:**', ["Admin", "Usuário"])

        if hierarquia_atividade == "Admin":
            # Menu no sidebar para Admin
            admin_menu = st.sidebar.radio("**Selecione uma opção abaixo:**",["Dashboard", "Usuários", "Produtos", "Templates"],key='admin_menu')

            if admin_menu == "Dashboard":
                st.header("Dashboard")
                st.warning("Em desenvolvimento...")
            elif admin_menu == "Usuários":
                cadastro_usuarios.gerenciamento_usuarios()
            elif admin_menu == "Produtos":
                st.header("Cadastro de Produtos")
                cadastro_produtos.gerenciamento_produtos()
            elif admin_menu == "Templates":
                st.header("Cadastro de Templates")
                cadastro_templates.gerenciamento_templates()

        elif hierarquia_atividade == "Usuário":
            # Menu no sidebar para Usuário

            usuario_ativo = f'{st.session_state["name"]} ({st.session_state["email"]})'
            user_menu = st.sidebar.radio("**Selecione uma opção abaixo:**", ["Dashboard", "Empresas", "Contatos", "Leads", "Oportunidades"], key="user_menu")

            if user_menu == "Dashboard":
                st.header("Dashboard")
                st.warning("Em desenvolvimento...")
            elif user_menu == "Empresas":
                cadastro_empresas.gerenciamento_empresas(usuario_ativo)
            elif user_menu == "Contatos":
                cadastro_contatos.gerenciamento_contatos()
            elif user_menu == "Leads":
                cadastro_leads.gerenciamento_leads()
            elif user_menu == "Oportunidades":
                cadastro_oportunidades.gerenciamento_oportunidades()
