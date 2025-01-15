import streamlit as st
from modules import cadastro_usuarios, cadastro_empresas, cadastro_produtos, cadastro_oportunidades, cadastro_templates, cadastro_contatos, cadastro_orcamentos, cadastro_subempresas, cadastro_leads

# Configuração da página principal
st.set_page_config(
    page_title="Gerenciador de Cadastros",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Gerenciador de Cadastros")

# Configurar as abas
tabs = st.tabs(["Usuários", "Empresas (Matriz)","Empresas (Sub-empresas)", "Produtos", "Templates", "Contatos", "Leads","Oportunidades","Orçamentos"])

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