import streamlit as st
import time
import os, sys
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.login_functions import (
    authenticate_user,
    change_password,
    send_reset_code,
    change_user_password,
    verify_reset_code,
    get_client_ip,
    get_user_agent,
    log_login_attempt,
    send_message_id,
)


# 로그인 함수
def login_main_ui():
    with st.sidebar:
        st.write("🔒 **로그인이 필요합니다.**")
        with st.form(key="login_form"):
            username = st.text_input("사용자 이름", key="username_input")
            password = st.text_input("비밀번호", type="password", key="password_input")
            submit_button = st.form_submit_button("로그인")
        st.session_state.update(
            {
                "last_active": time.time(),
                "username": username,
                "client_ip": get_client_ip(),
                "user_agent": get_user_agent(),
            }
        )
        if submit_button:
            if not username:
                st.error("사용자 이름을 입력하세요.")
                return
            success, message, role = authenticate_user(username, password)
            if success:
                st.session_state.update(
                    {
                        "authenticated": True,
                        "role": role,
                    }
                )
                st.success(f"{username}님, 로그인 성공!")
                log_login_attempt(
                    st.session_state["username"],
                    "success",
                    st.session_state["client_ip"],
                    st.session_state["user_agent"],
                )
                time.sleep(1)
                st.rerun()
            else:
                log_login_attempt(
                    st.session_state["username"],
                    "failure",
                    st.session_state["client_ip"],
                    st.session_state["user_agent"],
                )
                st.error(message)  # 로그인 실패 사유 출력


# 비밀번호 변경 함수
def change_password_ui():
    with st.sidebar:
        st.write("🔑 **비밀번호 변경**")
        with st.form(key="change_password_form"):
            username = st.text_input("사용자 이름", key="username_change_input")
            old_password = st.text_input(
                "기존 비밀번호", type="password", key="old_password_input"
            )
            new_password = st.text_input(
                "새 비밀번호", type="password", key="new_password_input"
            )
            new_password_retype = st.text_input(
                "비밀번호 번호재입력", type="password", key="new_password_retype"
            )
            submit_button = st.form_submit_button("비밀번호 변경")
        if submit_button:
            success, message = change_password(
                username, old_password, new_password, new_password_retype
            )
            if success:
                st.success(message)
                st.session_state["change_step"] = "finish_password"
                time.sleep(1)
                st.session_state.clear()
                st.rerun()
            else:
                st.warning(message)


def check_session_timeout():
    if "last_active" in st.session_state:
        if time.time() - st.session_state["last_active"] > 1800:  # 30분(1800초) 제한
            st.session_state.clear()
            st.warning("세션이 만료되었습니다. 다시 로그인 해주세요.")
            st.rerun()  # 바로 로그인 창으로 이동
    return True  # 활성 세션 유지


def send_reset_code_ui():
    """비밀번호 재설정 코드 요청 UI"""
    with st.sidebar:
        st.write("📩 비밀번호 찾기")
        with st.form(key="forgot_password_form"):
            username = st.text_input("사용자 이름", key="forgot_username")
            submit_button = st.form_submit_button("인증 코드 보내기")
        if submit_button:
            checker, result_message = send_reset_code(
                username=username
            )  # DB에서 코드 생성 및 전송
            if checker == True:
                st.success(result_message)
                st.session_state["reset_step"] = (
                    "verify_code"  # 인증 코드 확인 단계로 이동
                )
                st.session_state["reset_username"] = username  # 사용자 이름 저장
                st.rerun()
            else:
                st.error(result_message)


def reset_password_ui():
    """비밀번호 재설정 UI (인증 코드 입력 후 비밀번호 설정)"""
    with st.sidebar:
        st.write("🔑 비밀번호 재설정")
        username = st.session_state.get("reset_username", "")
        st.write(f"{username}님, 비밀번호 재설정")
        if st.session_state.get("reset_step") == "verify_code":
            with st.form(key="reset_password_form"):
                reset_code = st.text_input("인증 코드 입력", key="reset_code")
                submit_button = st.form_submit_button("인증 코드 확인")
            if submit_button:
                if verify_reset_code(
                    username=username, reset_code=reset_code
                ):  # 인증 코드 확인
                    st.session_state["reset_step"] = "set_password"  # 다음 단계 설정
                    st.success("인증 완료! 새 비밀번호를 설정하세요.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("인증 코드가 올바르지 않습니다.")

        elif st.session_state.get("reset_step") == "set_password":
            st.markdown("새 비밀번호를 설정하세요.")
            with st.form(key="set_new_password_form"):
                new_password = st.text_input(
                    "새 비밀번호", type="password", key="new_password"
                )
                new_password_retype = st.text_input(
                    "새 비밀번호 확인", type="password", key="new_password_retype"
                )
                submit_button = st.form_submit_button("비밀번호 변경")

            if submit_button:
                if new_password != new_password_retype:
                    st.error("새 비밀번호가 일치하지 않습니다.")
                else:
                    result_message = change_user_password(username, new_password)

                    if result_message == "비밀번호 변경 완료!":
                        st.success(result_message)
                        time.sleep(1)
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.error(result_message)


def send_reset_code_with_email_ui():
    """아이디찾기기 코드 요청 UI"""
    with st.sidebar:
        st.write("🔑 아이디 찾기")
        with st.form(key="forgot_password_form"):
            email = st.text_input("회사 이메일", key="forgot_useremail")
            submit_button = st.form_submit_button("인증 코드 보내기")
        if submit_button:
            checker, result_message = send_reset_code(
                email=email
            )  # DB에서 코드 생성 및 전송
            if checker == True:
                st.success(result_message)
                st.session_state["find_step"] = (
                    "verify_code"  # 인증 코드 확인 단계로 이동
                )
                st.session_state["find_email"] = email  # 사용자 이름 저장

                st.rerun()
            else:
                st.error(result_message)


def find_id_ui():
    with st.sidebar:
        st.write("🔑 아이디 찾기")
        email = st.session_state.get("find_email", "")
        st.write(f"{email}님, 아이디 찾기")
        if st.session_state.get("find_step") == "verify_code":
            with st.form(key="find_id_form"):
                reset_code = st.text_input("인증 코드 입력", key="reset_code")
                submit_button = st.form_submit_button("인증 코드 확인")
            if submit_button:
                if verify_reset_code(
                    email=email, reset_code=reset_code
                ):  # 인증 코드 확인
                    state, message = send_message_id(email)
                    if state:
                        st.success(message)
                        time.sleep(1)
                        countdown_placeholder = st.empty()
                        for i in range(5, 0, -1):
                            countdown_placeholder.info(
                                "로그인 페이지로 이동합니다. %d초 후 이동합니다." % i
                            )
                            time.sleep(1)
                        st.session_state["find_step"] = None
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.error(
                            "두레이 API에 문제가 있습니다. 관리자에게 문의주세요.",
                            message,
                        )
                else:
                    st.error("인증 코드가 올바르지 않습니다.")


# 로그아웃 함수
def logout():
    for key in ["authenticated", "username", "last_active"]:
        if key in st.session_state:
            del st.session_state[key]
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()
