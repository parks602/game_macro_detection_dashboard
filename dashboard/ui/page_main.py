import streamlit as st
import sys
from page_login import login
from page_dashboard import ro1_macro_dashbaord
from page_admin import admin
from utils.ui_config import configure_streamlit
from utils.exception_handler import global_exception_handler, error_page

configure_streamlit()

sys.excepthook = global_exception_handler


if "error" not in st.session_state:
    st.session_state["error"] = False
if "download_raw_data" not in st.session_state:
    st.session_state["download_raw_data"] = None
if "download_raw_data_list" not in st.session_state:
    st.session_state["download_raw_data_list"] = None
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "download" not in st.session_state:
    st.session_state["download"] = False
if "download_data" not in st.session_state:
    st.session_state["download_data"] = False
if "change_step" not in st.session_state:
    st.session_state["change_step"] = None
if "reset_step" not in st.session_state:
    st.session_state["reset_step"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "reset_username" not in st.session_state:
    st.session_state["reset_username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "page" not in st.session_state:
    st.session_state["page"] = None
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = None
if "admin_selected_page" not in st.session_state:
    st.session_state["admin_selected_page"] = None
if "macro_date" not in st.session_state:
    st.session_state["macro_date"] = None
if "user_aid" not in st.session_state:
    st.session_state["user_aid"] = None
if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = "로그인"
if "selected_ip" not in st.session_state:
    st.session_state["selected_ip"] = None
if "selected_start_date" not in st.session_state:
    st.session_state["selected_start_date"] = None
if "selected_end_date" not in st.session_state:
    st.session_state["selected_end_date"] = None
    
if "graph_generating" not in st.session_state:
    st.session_state["graph_generating"] = {'second':False, 'minute':False, 'seconds':False}

    
if st.session_state["error"]:
    error_page()

if st.session_state["authenticated"] == False:
    login()

elif st.session_state["authenticated"]:
    if st.session_state["role"] == "user":
        page_options = ["RO1 대시보드"]
    elif st.session_state["role"] == "admin":
        page_options = ["RO1 대시보드", "관리자 페이지"]

    if page_options:
        with st.sidebar:
            st.title("대시보드 선택")
            selected_page = st.selectbox("이동할 페이지 선택", page_options)
            st.session_state["page"] = selected_page

    if st.session_state["page"] in ["RO1 대시보드"]:
        ro1_macro_dashbaord()
    elif st.session_state["page"] == "로그인":
        login()
    elif st.session_state["page"] in ["관리자 페이지"]:
        admin()
