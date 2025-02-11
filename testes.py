import streamlit as st

st.title("CRM Hygge with Microsoft Login")

# 1) Check if user is logged in
if not st.experimental_user.is_logged_in:
    # 2) Trigger Microsoft login (matches [auth.microsoft] in secrets.toml)
    st.login("microsoft")
else:
    # 3) User is logged in
    st.write(f"Hello, {st.experimental_user.name}!")
    st.write("You are now authenticated via Microsoft Azure AD.")
    
    # Optionally, show more user info:
    st.write("Email:", st.experimental_user.email)
    st.write("ID:", st.experimental_user.user_id)
