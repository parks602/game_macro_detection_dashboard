import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.exception_handler import global_exception_handler

from components.login.comp_login import login_form
from components.login.comp_ch_pwd import change_pwd_form
from components.login.comp_find_pwd import find_pwd_form


def login(
    cookie_manager,
    login_title: str = "로그인",
    change_title: str = "비밀번호 변경",
    find_id_title: str = "아이디 찾기",
    find_pwd_title: str = "비밀번호 찾기",
):
    PAGES = {
        login_title: login_form,
        change_title: change_pwd_form,
        find_id_title: None,
        find_pwd_title: find_pwd_form,
    }

    try:
        with st.sidebar:
            tab_options = [login_title, change_title, find_id_title, find_pwd_title]
            selected_tab = st.radio(
                "탭 선택",
                tab_options,
                index=tab_options.index(st.session_state.selected_tab),
            )
            if st.session_state.selected_tab != selected_tab:
                login_temp_states = ["change_step", "reset_step", "reset_username"]
                for state in login_temp_states:
                    if state in st.session_state:
                        st.session_state[state] = None

                st.session_state["selected_tab"] = selected_tab
                st.rerun()
        # subheader 텍스트
        blank1, con1, black2 = st.columns([2, 5, 2])
        with con1:
            st.markdown(
                '<h3 style="text-align: center;">✨ 그라비티 데이터 분석 센터 ✨</h3>',
                unsafe_allow_html=True,
            )
            st.success(
                "로그인이 필요합니다. 계정이 없을 경우 플랫폼개발Unit에 문의하세요."
            )

            with st.container(height=600):
                if selected_tab in PAGES:
                    form_function = PAGES[selected_tab]
                    if form_function == login_form:
                        form_function(cookie_manager)
                    elif selected_tab == find_id_title:
                        st.info(
                            "아이디 찾기는 보안상 제공되지 않습니다. 관리자에게 문의 부탁드립니다."
                        )
                    else:
                        form_function()
                else:
                    st.error("선택한 페이지를 찾을 수 없습니다. 관리자에게 문의하세요.")

    except Exception as e:
        global_exception_handler(e)
