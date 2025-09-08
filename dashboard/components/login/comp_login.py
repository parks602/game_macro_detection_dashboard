import streamlit as st
import time
from funcitons.login.login_function import (
    validate_input_and_password,
    get_db_connection,
    authenticate_system,
    check_fail_login,
)


def login_form(
    cookie_manager,
    login_username_label: str = "ID를 입력하세요",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "비밀번호를 입력하세요",
    login_password_placeholder: str = None,
    login_password_help: str = "Password cannot be recovered if lost",
    login_button_label: str = "login account",
):
    client = get_db_connection()
    with st.form(key="login"):
        username = st.text_input(
            label=login_username_label,
            placeholder=login_username_placeholder,
            help=login_username_help,
        )

        password = st.text_input(
            label=login_password_label,
            placeholder=login_password_placeholder,
            help=login_password_help,
            type="password",
        )

        if st.form_submit_button(
            label=login_button_label,
            type="primary",
            use_container_width=True,
        ):
            success, role = authenticate_system(username, password, client)
            if success == True:
                client.disconnect_from_db()
                st.session_state.update(
                    {"authenticated": True, "role": role, "user_name": username}
                )
                cookie_manager.save_login_to_cookie(username, role)
                st.success(f"🎉 {username}님, 로그인 성공!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("로그인 정보가 올바르지 않습니다.")
                if not check_fail_login(username, client):
                    st.error("로그인 실패 횟수 초과로 로그인이 30분간 차단됩니다.")
