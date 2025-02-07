import streamlit as st

# CSS atualizado para adicionar rolagem ao conteúdo do st.expander
css = """
<style>
    /* Aplica rolagem ao conteúdo dentro dos expanders */
    div[data-testid="stExpanderDetails"] {
        max-height: 400px !important;  /* Altura máxima antes do scroll */
        overflow-y: auto !important;  /* Força a rolagem vertical */
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Criando expanders com muito conteúdo para testar a rolagem
for i in range(3):
    with st.expander(f"📋 Ver mais - Expander {i+1}"):
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 50)
