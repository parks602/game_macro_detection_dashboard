import streamlit as st
from components.admin.comp_admin import create_user_form
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.exception_handler import global_exception_handler

def admin():
    try:
        bl1, col, bl2 = st.columns([3, 5, 3])
        with col:
            create_user_form()
    except Exception as e:
        global_exception_handler(e)
