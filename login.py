import streamlit as st
from modules import cadastro_usuarios, cadastro_empresas, cadastro_produtos, cadastro_oportunidades, cadastro_templates, cadastro_contatos, cadastro_orcamentos

# Configuração da página principal
st.set_page_config(
    page_title="Gerenciador de Cadastros",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Gerenciador de Cadastros")

# Configurar as abas
tabs = st.tabs(["Usuários", "Empresas", "Produtos", "Templates"])

# Aba: Cadastro de Usuários
with tabs[0]:
    st.header("Cadastro de Usuários")
    cadastro_usuarios.cadastro_usuarios()

# Aba: Cadastro de Empresas
with tabs[1]:
    st.header("Cadastro de Empresas")
    cadastro_empresas.cadastro_empresas()

# Aba: Cadastro de Produtos
with tabs[2]:
    st.header("Cadastro de Produtos")
    cadastro_produtos.cadastro_produtos()

with tabs[3]:
    st.header("Cadastro de Templates")
    cadastro_templates.gerenciamento_templates()