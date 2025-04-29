import streamlit as st
from funcitons.admin.user_creator import register_user


def create_user_form(
    create_user_name_label: str = "사용자 ID",
    create_user_name_placeholder: str = None,
    create_user_name_help: str = None,
    create_user_password_label: str = "사용자 비밀번호",
    create_user_password_placeholder: str = None,
    create_user_password_help: str = None,
    create_user_email_label: str = "사용자 E-mail",
    create_user_email_placeholder: str = None,
    create_user_email_help: str = None,
    create_user_role_label: str = "사용자 Role",
    create_user_role_placeholder: str = None,
    create_user_role_help: str = None,
    create_button_label: str = "Create User",
):
    st.subheader("유저 생성")
    with st.form(key="create user"):
        username = st.text_input(
            label=create_user_name_label,
            placeholder=create_user_name_placeholder,
            help=create_user_name_help,
        )

        password = st.text_input(
            label=create_user_password_label,
            placeholder=create_user_password_placeholder,
            help=create_user_password_help,
            type="password",
        )

        email = st.text_input(
            label=create_user_email_label,
            placeholder=create_user_email_placeholder,
            help=create_user_email_help,
        )

        role = st.text_input(
            label=create_user_role_label,
            placeholder=create_user_role_placeholder,
            help=create_user_role_help,
        )
        if st.form_submit_button(
            label=create_button_label,
            type="primary",
            use_container_width=True,
        ):
            key, message = register_user(username, password, email, role)
            if key:
                st.success(message)
            if not key:
                st.error(message)
