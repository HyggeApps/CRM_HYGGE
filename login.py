import streamlit as st
import msal
from msal import ConfidentialClientApplication
import requests
import smtplib

# Verifique se a sessão já tem uma chave 'logado'
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    st.title("Bem-vindo(a) ao ambiente integrado da Hygge!")
    st.info("A finalidade desta plataforma integrada é estabelecer uma ponte eficaz entre os diversos departamentos da Hygge, promovendo um núcleo unificado para a criação e gerenciamento de propostas, organização de pastas, composição de e-mails, realização de simulações e elaboração de relatórios. \nEfetue o seu acesso por meio da aba lateral e adote o nosso lema: **\"Be Efficient. Be Better. Be Hygge.\"**")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown('------')

    
    
    CLIENT_ID = '2416c40e-33c3-4632-9f43-1884815ceeb8'
    CLIENT_SECRET = '4Lz8Q~0aKVTfTfcWu0h1UWG1FmbiZt-uzGKMlbzL'
    TENANT_ID = '68c8d20f-fecd-4b5c-bf1b-8def71adada1'
    AUTHORITY_URL = f'https://login.microsoftonline.com/{TENANT_ID}'
    SCOPE = ['https://graph.microsoft.com/.default']
    # Criar uma instância de aplicação
    app = ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY_URL, client_credential=CLIENT_SECRET)

    # Adquirir token
    result = app.acquire_token_for_client(scopes=SCOPE)

    

    if "access_token" in result:
        # Usar o token de acesso para chamar o Microsoft Graph API
        token = result['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        url = 'https://graph.microsoft.com/v1.0/users'
        response = requests.get(url, headers=headers)
        users = response.json()
        emails = []
        for user in users.get('value', []):
            # Imprimir o endereço de e-mail do usuário
            emails.append(user.get('mail', 'No email found'))
    else:
        print(result.get("error"))
        print(result.get("error_description"))
    

    #st.sidebar.error('EM MANUTENÇÃO, AGUARDE...')
    #emails = ['rodrigo@hygge.eco.br']

    if 'AgendadoMatheus@hygge.eco.br' in emails:
        emails.remove('AgendadoMatheus@hygge.eco.br')
    if 'FabricioHygge@hygge.eco.br' in emails:
        emails.remove('FabricioHygge@hygge.eco.br')
    if 'ThiagoHygge@hygge.eco.br' in emails:
        emails.remove('ThiagoHygge@hygge.eco.br')

    email_principal = st.sidebar.selectbox("Email", emails)
    senha_principal = st.sidebar.text_input("Senha", type="password")
    
    # If the user is not logged in, show the login button and login process
    if st.sidebar.button('Entrar'):
        try:
            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login(email_principal, senha_principal)
            st.sidebar.success("Login realizado com sucesso!")
            
            # Update the session state to logged in
            st.session_state['logado'] = True
            st.session_state['email_principal'] = email_principal
            st.session_state['senha_principal'] = senha_principal
            
        except Exception as e:
            st.sidebar.error("Falha no login.")

# This part is executed if the user is logged in - LOGIN DO USUÁRIO
if st.session_state.get('logado', False):
    nome_user = st.session_state['email_principal'].replace("@hygge.eco.br", "")
    email_principal = st.session_state['email_principal']
    st.sidebar.markdown('------')
    
    if any(user in email_principal for user in ['rodrigo', 'alexandre', 'paula', 'fabricio','admin']):
        opcao_servico = st.sidebar.radio(
            label=f'**Olá {nome_user.upper()}, o que você deseja fazer?**',
            options=('-- Selecione uma das opções --', 'Geração e envio de propostas', 'Criação de pastas e envios de aceite', 'Envio do email de boas-vindas', 'Envio do relatório/entregável HYGGE'),
            index=0  # This sets 'Propostas' as the default value
        )
    elif any(user in email_principal for user in ['matheus', 'comercial']):
        opcao_servico = st.sidebar.radio(
            label=f'**Olá {nome_user.upper()}, o que você deseja fazer?**',
            options=('-- Selecione uma das opções --', 'Geração e envio de propostas', 'Criação de pastas e envios de aceite'),
            index=0  # This sets 'Propostas' as the default value
        )