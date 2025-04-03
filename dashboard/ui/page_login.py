import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.exception_handler import global_exception_handler

from components.login.comp_login import login_form
from components.login.comp_ch_pwd import change_pwd_form
from components.login.comp_find_pwd import find_pwd_form


def login(
    login_title: str = "로그인",
    change_title: str = "비밀번호 변경",
    find_id_title: str = "아이디 찾기",
    find_pwd_title: str = "비밀번호 찾기",
):
    try:
        with st.sidebar:
            tab_options = [login_title, change_title, find_id_title, find_pwd_title]
            selected_tab = st.radio("탭 선택", tab_options, index=tab_options.index(st.session_state.selected_tab))
            if st.session_state.selected_tab != selected_tab:
                st.session_state.clear()
                st.session_state.selected_tab = selected_tab
                st.rerun()
        # subheader 텍스트
        blank1, con1, black2 = st.columns([2, 5, 2])
        with con1:
            st.markdown(
                '<h3 style="text-align: center;">✨ 그라비티 데이터 분석 센터 ✨</h3>',
                unsafe_allow_html=True,
            )
            st.success("로그인이 필요합니다. 계정이 없을 경우 플랫폼개발Unit에 문의하세요.")

            with st.container(height=600):
                if selected_tab == login_title:
                    login_form()
                    st.info("로그인 반복 실패시 로그인 기능이 차단됩니다.")
                elif selected_tab == change_title:
                    change_pwd_form()
                elif selected_tab == find_id_title:
                    st.info(
                        "아이디 찾기는 보안상 제공되지 않습니다. 관리자에게 문의 부탁드립니다."
                    )
                elif selected_tab == find_pwd_title:
                    find_pwd_form()
    except Exception as e:
        global_exception_handler(e)
