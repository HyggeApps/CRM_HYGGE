import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import streamlit as st
from modules import (
    usuarios,
    empresas,
    tarefas,
    meus_numeros,
    contatos,
    cadastro_produtos,
    cadastro_oportunidades,
    templates,
    cadastro_orcamentos,
    cadastro_leads
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
from streamlit_option_menu import option_menu


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


# Configuração da página
st.set_page_config(
    page_title='CRM HYGGE', layout='wide',
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

st.markdown(
    """
    <style>
    .stForm {
        width: 95% !important; /* Ajusta a largura do formulário */
        margin: auto; /* Centraliza o formulário */
        padding: 10px; /* Adiciona mais espaço interno */
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
        font-size: 2.75rem !important; /* Tamanho para H1 */
    }
    h2 {
        font-size: 2.5rem !important; /* Tamanho para H2 */
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

# Adicionando CSS personalizado para ajustar o tamanho da fonte
st.markdown(
    """
    <style>
    /* Ajustar o tamanho da fonte do menu */
    .nav-link {
        font-size: 8px !important; /* Tamanho da fonte desejado */
    }
    .nav-link i {
        font-size: 10px !important; /* Ajustar o tamanho do ícone, se necessário */
    }
    </style>
    """,
    unsafe_allow_html=True,
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
        usuario_ativo = f'{st.session_state["name"]} ({st.session_state["email"]})'
        if 'admin' in st.session_state["roles"]:
            
            st.info(f'Bem-vindo(a), **{st.session_state["name"]}**!')
            st.info('Este é o ambiente de **admin** para consulta, preenchimento, controle e envio das informações referentes as oportunidades da HYGGE.')
        
            # 1. as sidebar menu
            selected = option_menu(
                f"CRM HYGGE (Admin)",
                ["Tarefas", "Empresas", "Contatos", "Negócios", "Templates", "Produtos", "Usuários"],
                icons=["list-task", "building", "person-lines-fill", "currency-dollar", "file-earmark-text", "archive", "person-add"],
                menu_icon="cast",
                default_index=0,
                styles={
                    #"container": {"background-color": "#3C353F"},  # Background color for the entire menu
                    "menu-title": {"font-size": "16px", "font-weight": "bold"},  # Title styling
                    "nav-link": {"font-size": "12px"},  # Style for links
                    "nav-link-selected": {"font-size": "12px"},  # Style for the selected link
                },
            )
        else:
            
            st.info(f'Bem-vindo(a), **{st.session_state["name"]}**!')
            st.info('Este é o ambiente de **vendedor** para consulta, preenchimento, controle e envio das informações referentes as oportunidades da HYGGE.')

            # 1. as sidebar menu
            selected = option_menu(
                f"CRM HYGGE (Admin)",
                ["Tarefas", "Empresas", "Contatos", "Negócios", "Templates", "Produtos", "Usuários"],
                icons=["list-task", "building", "person-lines-fill", "currency-dollar", "file-earmark-text", "archive", "person-add"],
                menu_icon="cast",
                default_index=0,
                styles={
                    #"container": {"background-color": "#3C353F"},  # Background color for the entire menu
                    "menu-title": {"font-size": "16px", "font-weight": "bold"},  # Title styling
                    "nav-link": {"font-size": "12px"},  # Style for links
                    "nav-link-selected": {"font-size": "12px"},  # Style for the selected link
                },
            )

    elif st.session_state['authentication_status'] is False:
        st.error('Usuário e/ou Senha inválido(s).')
    elif st.session_state['authentication_status'] is None:
        st.warning('Por favor, entre com o seu usuário e senha.')


if st.session_state['authentication_status']:    
    usuario_ativo = f'{st.session_state["name"]} ({st.session_state["email"]})'
    # Título Principal
    st.title("🗒️ *Customer Relationship Management* (CRM) - HYGGE")
    st.write('----')

    if selected == "Tarefas":
        st.header("📜 Tarefas")
        st.info('Acompanhe aqui suas tarefas e seus números.')

        tela_tarefas, tela_stats = st.tabs(['Minhas tarefas', 'Meus números'])
        with tela_tarefas:
            if 'admin' in st.session_state["roles"]: tarefas.gerenciamento_tarefas_por_usuario(usuario_ativo,admin=True)
            else: tarefas.gerenciamento_tarefas_por_usuario(usuario_ativo,admin=False)
        with tela_stats:
            st.write(1)
            #meus_numeros.compilar_meus_numeros(usuario_ativo)
    elif selected == "Empresas":
        st.header("🏢 Empresas")
        st.info('Consulte, cadastre e edite suas empresas.')
        st.write('----')

        with st.popover("➕ Cadastrar empresa"):
            if 'admin' in st.session_state["roles"]: empresas.cadastrar_empresas(usuario_ativo,admin=True)
            else: empresas.cadastrar_empresas(usuario_ativo,admin=False)

        if 'admin' in st.session_state["roles"]:  empresas.consultar_empresas(usuario_ativo, admin=True)
        else: empresas.consultar_empresas(usuario_ativo, admin=False)

        
    elif selected == 'Contatos':
        st.header("📞 Contatos")
        st.info('Consulte contatos aqui.')
        st.warning("⚠️ IMPORTANTE: O cadastro de contatos deve ser feito a partir da tela da 'Empresas'")
        st.write('----')
        contatos.exibir_todos_contatos_empresa()

    elif selected == 'Templates':
        if 'admin' in st.session_state["roles"]: templates.gerenciamento_templates()
        else: st.warning("Você não tem permissão para alterar templates.")

    elif selected == 'Usuários':
        if 'admin' in st.session_state["roles"]: usuarios.gerenciamento_usuarios()
        else: st.warning("Você não tem permissão para alterar usuários.")

