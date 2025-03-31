import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.login.comp_login import login_form
from components.login.comp_ch_pwd import change_pwd_form
from components.login.comp_find_pwd import find_pwd_form


def login(
    login_title: str = "로그인",
    change_title: str = "비밀번호 변경",
    find_id_title: str = "아이디 찾기",
    find_pwd_title: str = "비밀번호 찾기",
):
    # subheader 텍스트
    blank1, con1, black2 = st.columns([3, 5, 3])
    with con1:
        st.markdown(
            '<h3 style="text-align: center;">✨ 그라비티 데이터 분석 센터 ✨</h3>',
            unsafe_allow_html=True,
        )
        st.success("로그인이 필요합니다. 계정이 없을 경우 플랫폼개발Unit에 문의하세요.")
        with st.container(height=600):
            login_tab, change_pwd, find_id, find_pwd = st.tabs(
                [login_title, change_title, find_id_title, find_pwd_title]
            )
            with login_tab:
                login_form()
                st.info("로그인 반복 실패시 로그인 기능이 차단됩니다.")
            with change_pwd:
                change_pwd_form()
            with find_id:
                st.info(
                    "아이디 찾기는 보안상 제공되지 않습니다. 관리자에게 문의 부탁드립니다."
                )
            with find_pwd:
                find_pwd_form()
