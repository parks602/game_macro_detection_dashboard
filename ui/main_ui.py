import streamlit as st
import sys, os
from ui_utils import configure_streamlit

configure_streamlit()

from dashboard_summary_ui import dashboard_summary
from dashboard_cosine_sim import dashboard_cos_sim
from dashboard_self_sim import dashboard_self_sim
from dashboard_same_time_diff_action import dashboard_same_time_diff_action
from dashboard_macro_CS import dashboard_CS
from dashboard_user_search import dashboard_user_detail
from dashboard_same_time_same_action import dashboard_same_time_same_action
import traceback

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from login_ui import (
    login_main_ui,
    change_password_ui,
    send_reset_code_with_email_ui,
    find_id_ui,
    send_reset_code_ui,
    reset_password_ui,
    check_session_timeout,
    logout,
)
from admin_ui import admin


def global_exception_handler(error_msg):
    """
    통합 에러 페이지를 출력하는 함수.
    """
    st.error("예상치 못한 오류가 발생했습니다. 관리자에게 문의하세요.")
    st.text_area("오류 상세 정보", error_msg, height=200)
    st.stop()


# 전역 예외 핸들러 설정
sys.excepthook = lambda etype, e, tb: global_exception_handler(
    "".join(traceback.format_exception(etype, e, tb))
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if "client_ip" not in st.session_state:
    st.session_state["client_ip"] = None

if "user_agent" not in st.session_state:
    st.session_state["user_agent"] = None

if "timestamp" not in st.session_state:
    st.session_state["timestamp"] = None

if "change_step" not in st.session_state:
    st.session_state["change_step"] = None

if "find_step" not in st.session_state:
    st.session_state["find_step"] = None

if "reset_step" not in st.session_state:
    st.session_state["reset_step"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "로그인"

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page2" not in st.session_state:
    st.session_state["page2"] = "로그인"

if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = None

try:
    # 인증되지 않은 사용자 페이지 처리
    if not st.session_state["authenticated"]:
        with st.sidebar:
            page_selected = st.selectbox(
                "선택하세요",
                ["로그인", "비밀번호 변경", "아이디 찾기", "비밀번호 찾기"],
                index=["로그인", "비밀번호 변경", "아이디 찾기", "비밀번호 찾기"].index(
                    st.session_state["page"]
                ),  # 현재 선택된 페이지 유지
            )
        if page_selected != st.session_state["page"]:
            st.session_state["page"] = page_selected
            st.rerun()

        if st.session_state["page"] == "로그인":
            login_main_ui()
        elif st.session_state["page"] == "비밀번호 변경":
            if st.session_state["change_step"] == None:
                change_password_ui()  # 기존 비밀번호 알고 있는 경우
            elif st.session_state["change_step"] == "finish_password":
                st.session_state["page"] = "로그인"
                st.session_state.clear()
                st.rerun()

        elif st.session_state["page"] == "아이디 찾기":
            if st.session_state["find_step"] == None:
                send_reset_code_with_email_ui()
            elif st.session_state["find_step"] == "verify_code":
                find_id_ui()

        elif st.session_state["page"] == "비밀번호 찾기":
            if st.session_state["reset_step"] == None:
                send_reset_code_ui()
            elif st.session_state["reset_step"] in ["verify_code", "set_password"]:
                reset_password_ui()

    # 인증된 사용자 페이지 처리
    else:
        if not check_session_timeout():  # ⏳ 세션 타임아웃 체크
            st.session_state["authenticated"] = False
        with st.sidebar:
            st.title("메뉴 선택")
            if st.session_state["role"] == "admin":
                page_options = ["대시보드", "관리자 페이지"]
            elif st.session_state["role"] == "user":
                page_options = ["대시보드"]
            else:
                st.write("권한이 없습니다.")
                page_options = []
            selected_page = st.selectbox("이동할 페이지 선택", page_options)
            st.session_state["page2"] = selected_page
            st.write("---")
            if st.button("로그아웃"):
                logout()

        if st.session_state["page2"] == "대시보드":
            # 대시보드 내에서 기본 페이지 또는 세부 페이지 선택
            dashboard_options = [
                "RO1 매크로 현황",
                "유저 세부 사항",
                "0. 대시보드 요약",
                "1. 멀티 클라이언트-(같은행위)",
                "2. 멀티 클라이언트-(다른행위)",
                "3. 코사인 유사도",
                "4. 자기 유사도",
            ]  # 선택할 세부 페이지 추가
            selected_dashboard = st.selectbox(
                "대시보드 세부 페이지 선택", dashboard_options
            )

            # 선택된 세부 페이지에 따라 해당 페이지 로드
            if selected_dashboard == "RO1 매크로 현황":
                dashboard_CS()
            elif selected_dashboard == "유저 세부 사항":
                dashboard_user_detail()
            elif selected_dashboard == "0. 대시보드 요약":
                dashboard_summary()  # 대시보드 요약 함수
            elif selected_dashboard == "1. 멀티 클라이언트-(같은행위)":
                dashboard_same_time_same_action()
            elif selected_dashboard == "2. 멀티 클라이언트-(다른행위)":
                dashboard_same_time_diff_action()
            elif selected_dashboard == "3. 코사인 유사도":
                dashboard_cos_sim()  # 코사인 유사도 대시보드 함수
            elif selected_dashboard == "4. 자기 유사도":
                dashboard_self_sim()  # 자기 유사도 대시보드 함수
        elif (
            st.session_state["page2"] == "관리자 페이지"
            and st.session_state["role"] == "admin"
        ):
            admin()
except Exception as e:
    global_exception_handler(traceback.format_exc())
