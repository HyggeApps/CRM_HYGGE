import streamlit as st
import streamlit_authenticator as stauth
import firebase_admin
from firebase_admin import credentials, db

# Inicialize o Firebase
cred = credentials.Certificate("firebase/crm-hygge-firebase-adminsdk-idxya-ee232e2954.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://crm-hygge-default-rtdb.firebaseio.com/'
})
# Funções para manipular usuários no banco de dados
def fetch_users():
    ref = db.reference('users')
    return ref.get() or {}

def save_user(username, email, name, password):
    ref = db.reference(f'users/{username}')
    ref.set({
        'email': email,
        'name': name,
        'password': password,
    })

# Obter credenciais do banco de dados
users = fetch_users()
credentials = {'usernames': {}}

for username, details in users.items():
    credentials['usernames'][username] = {
        'email': details['email'],
        'name': details['name'],
        'password': details['password'],
    }

# Configuração do autenticador
authenticator = stauth.Authenticate(
    credentials,
    'my_app_cookie',
    'abcdef',
    30,
)

# Interface do app
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.success(f'Bem-vindo, {name}!')
    st.write('Conteúdo protegido aqui...')
    if st.button('Logout'):
        authenticator.logout('Logout', 'main')

elif authentication_status is False:
    st.error('Usuário ou senha incorretos.')

elif authentication_status is None:
    st.warning('Por favor, insira seu nome de usuário e senha.')

# Interface de registro
with st.expander('Registrar novo usuário'):
    new_username = st.text_input('Usuário')
    new_email = st.text_input('E-mail')
    new_name = st.text_input('Nome completo')
    new_password = st.text_input('Senha', type='password')
    confirm_password = st.text_input('Confirme a senha', type='password')

    if st.button('Registrar'):
        if new_password == confirm_password:
            hashed_password = stauth.Hasher([new_password]).generate()[0]
            save_user(new_username, new_email, new_name, hashed_password)
            st.success('Usuário registrado com sucesso! Faça login.')
        else:
            st.error('As senhas não coincidem.')