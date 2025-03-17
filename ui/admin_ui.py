import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.login_functions import register_user

def admin():
    st.title("관리자 페이지")
    st.write(f"환영합니다, {st.session_state['username']}님!")

    st.subheader("계정 생성")
    with st.form(key="make_user"):
            mk_username = st.text_input("사용자 이름", key="username_input")
            mk_password = st.text_input("비밀번호", key="password_input")
            mk_email = st.text_input('사용자 email', key='email_input')
            mk_role = st.selectbox('사용자 ROLE', ['admin', 'user'])
            mk_submit_button = st.form_submit_button("유저 생성")
            if mk_submit_button:
                key, message = register_user(mk_username, mk_password, mk_email, mk_role)
                if key:
                    st.wirte(message)
                if not key:
                    st.wirte(message)
                
