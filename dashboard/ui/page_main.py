import streamlit as st
import os

from page_login import login
from page_dashboard import ro1_macro_dashbaord
from page_admin import admin
from utils.ui_config import configure_streamlit
from utils.exception_handler import configure_exception_handler

configure_streamlit()
configure_exception_handler()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True
if "change_step" not in st.session_state:
    st.session_state["change_step"] = None
if "reset_step" not in st.session_state:
    st.session_state["reset_step"] = None
if "reset_username" not in st.session_state:
    st.session_state["reset_username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = "admin"
if "page" not in st.session_state:
    st.session_state["page"] = None
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = None
if "admin_selected_page" not in st.session_state:
    st.session_state["admin_selected_page"] = None


if not st.session_state["authenticated"]:
    login()
elif st.session_state["role"] == "user":
    page_options = ["RO1 대시보드"]
elif st.session_state["role"] == "admin":
    page_options = ["로그인", "RO1 대시보드", "관리자 페이지"]

if "page_options" in locals() and page_options:
    with st.sidebar:
        st.title("대시보드 선택")
        selected_page = st.selectbox("이동할 페이지 선택", page_options)
        st.session_state["page"] = selected_page

if st.session_state["page"] in ["RO1 대시보드", None]:
    ro1_macro_dashbaord()
elif st.session_state["page"] == "로그인":
    login()
elif st.session_state["page"] in ["관리자 페이지", None]:
    admin()
