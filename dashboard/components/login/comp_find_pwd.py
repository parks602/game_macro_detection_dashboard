import streamlit as st
import time
from funcitons.login.login_function import (
    get_db_connection,
)
from funcitons.login.find_pwd_function import (
    send_reset_code,
    verify_reset_code,
    change_user_password,
)


def find_pwd_form():
    if st.session_state["reset_step"] == None:
        send_reset_code_form()
    elif st.session_state["reset_step"] == "verify_code":
        get_reset_code_form()
    elif st.session_state["reset_step"] == "set_password":
        set_password()


def send_reset_code_form(
    find_username_label: str = "ID를 입력하세요",
    find_username_placeholder: str = None,
    find_username_help: str = None,
    find_email_label: str = "사내 이메일을 입력하세요",
    find_email_placeholder: str = None,
    find_email_help: str = None,
    find_button_label: str = "인증번호 전송",
):
    client = get_db_connection()
    with st.form(key="find_password"):
        username = st.text_input(
            label=find_username_label,
            placeholder=find_username_placeholder,
            help=find_username_help,
        )

        email = st.text_input(
            label=find_email_label,
            placeholder=find_email_placeholder,
            help=find_email_help,
        )

        if st.form_submit_button(
            label=find_button_label,
            type="primary",
            use_container_width=True,
        ):
            checker, result_message = send_reset_code(
                username, email, client
            )  # DB에서 코드 생성 및 전송
            if checker == True:
                st.success(result_message)
                st.session_state["reset_step"] = "verify_code"
                st.session_state["reset_username"] = username  # 사용자 이름 저장
                st.rerun()
            else:
                st.error(result_message)

        st.info("두레이 메신저로 인증번호가 발송됩니다.")


def get_reset_code_form(
    resetcode_label: str = "메신저로 전송된 인증번호를 입력하세요",
    resetcode_placeholder: str = None,
    resetcode_help: str = None,
    resetcode_button_label: str = "인증번호 확인",
):
    client = get_db_connection()
    with st.form(key="verify_resetcode"):
        resetcode = st.text_input(
            label=resetcode_label,
            placeholder=resetcode_placeholder,
            help=resetcode_help,
        )
        if st.form_submit_button(
            label=resetcode_button_label,
            type="primary",
            use_container_width=True,
        ):
            message = verify_reset_code(
                st.session_state["reset_username"], resetcode, client
            )
            if message:  # 인증 코드 확인
                st.session_state["reset_step"] = "set_password"  # 다음 단계 설정
                st.success("인증 완료! 새 비밀번호를 설정하세요.")
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)


def set_password(
    new_password_label: str = "변경할 비밀번호를 입력하세요",
    new_password_placeholder: str = None,
    new_password_help: str = None,
    re_password_label: str = "비밀번호를 다시 입력하세요",
    re_password_placeholder: str = None,
    re_password_help: str = None,
    reset_button_label: str = "비밀번호 번경",
):
    client = get_db_connection()
    with st.form(key="rest_password"):
        new_password = st.text_input(
            label=new_password_label,
            placeholder=new_password_placeholder,
            help=new_password_help,
            type="password",
        )
        re_password = st.text_input(
            label=re_password_label,
            placeholder=re_password_placeholder,
            help=re_password_help,
            type="password",
        )
        if st.form_submit_button(
            label=reset_button_label,
            type="primary",
            use_container_width=True,
        ):
            if new_password != re_password:
                st.error("새 비밀번호가 일치하지 않습니다.")
            else:
                message = change_user_password(
                    st.session_state["reset_username"], new_password, client
                )
                if message==True:
                    client.disconnect_from_db()
                    st.success("비밀번호가 변경되었습니다. 로그인 해주세요")
                    time.sleep(1)
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error(message)
