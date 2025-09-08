import streamlit as st
import sys
from page_login import login
from page_dashboard import ro1_macro_dashbaord
from page_admin import admin
from utils.ui_config import configure_streamlit

configure_streamlit()


from utils.exception_handler import global_exception_handler, error_page
from utils.browser_handler import cookieAuth, LocalStorageManager,initialize_session_state


sys.excepthook = global_exception_handler

PAGE_OPTION_WITH_ROLE_DICT = {
    "user": ["RO1 대시보드"],
    "admin": ["RO1 대시보드", "관리자 페이지"],
}

PAGES = {
    "RO1 대시보드": ro1_macro_dashbaord,
    "로그인": login,
    "관리자 페이지": admin,
}

def get_cookie_manager():
    return cookieAuth()

def get_local_sotrage():
    return LocalStorageManager

cookie_manager = get_cookie_manager()
local_storage = get_local_sotrage()

cookie_manager.check_cookie_ready()

initialize_session_state(cookie_manager, local_storage)
cookie_manager.load_login_from_cookie()


if st.session_state["error"]:
    error_page()

if st.session_state["authenticated"] == False:
    login(cookie_manager)

elif st.session_state["authenticated"]:
    with st.sidebar:
        st.write(f"안녕하세요, {st.session_state['user_name']}님! 👋")
        if st.button("🚪 로그아웃"):
            cookie_manager.clear_all_cookies()
            initialize_session_state(cookie_manager, local_storage)
            st.rerun()
    page_options = PAGE_OPTION_WITH_ROLE_DICT.get(st.session_state["role"], [])

    if page_options:
        with st.sidebar:
            st.title("대시보드 선택")
            selected_page = st.selectbox("이동할 페이지 선택", page_options)
            st.session_state["page"] = selected_page

    if st.session_state["page"] in PAGES:
        PAGES[st.session_state["page"]]()
    else:
        st.error("선택한 페이지를 찾을 수 없습니다. 관리자에게 문의하세요.")
