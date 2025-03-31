import streamlit as st
from components.admin.comp_admin import create_user_form


def admin():
    bl1, col, bl2 = st.columns([3, 5, 3])
    with col:
        create_user_form()
