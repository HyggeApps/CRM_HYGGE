import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz

firebase_credentials = st.secrets["firebase2"]

st.write(firebase_credentials)