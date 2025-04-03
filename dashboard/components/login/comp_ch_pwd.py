import streamlit as st
import time
from funcitons.login.login_function import get_db_connection
from funcitons.login.change_pwd_function import change_password


def change_pwd_form(
    change_username_label: str = "ID를 입력하세요",
    change_username_placeholder: str = None,
    change_username_help: str = None,
    old_password_label: str = "기존 비밀번호를 입력하세요",
    old_password_placeholder: str = None,
    old_password_help: str = None,
    new_password_label: str = "새로운 비밀번호를 입력하세요",
    new_password_placeholder: str = None,
    new_password_help: str = None,
    re_new_password_label: str = "새로운 비밀번호를 다시 입력하세요",
    re_new_password_placeholder: str = None,
    re_new_password_help: str = None,
    change_button_label: str = "change password",
):
    client = get_db_connection()

    with st.form(key="change_password"):
        username = st.text_input(
            label=change_username_label,
            placeholder=change_username_placeholder,
            help=change_username_help,
        )

        password = st.text_input(
            label=old_password_label,
            placeholder=old_password_placeholder,
            help=old_password_help,
            type="password",
        )

        new_password = st.text_input(
            label=new_password_label,
            placeholder=new_password_placeholder,
            help=new_password_help,
            type="password",
        )

        re_new_password = st.text_input(
            label=re_new_password_label,
            placeholder=re_new_password_placeholder,
            help=re_new_password_help,
            type="password",
        )
        if st.form_submit_button(
            label=change_button_label,
            type="primary",
            use_container_width=True,
        ):
            success, message = change_password(
                username, password, new_password, re_new_password, client
            )
            if success == True:
                client.disconnect_from_db()
                st.success(message)
                st.session_state["change_step"] = "finish_password"
                st.session_state.selected_tab = "로그인"
                time.sleep(2)
                st.rerun()
            else:
                st.error(message)
