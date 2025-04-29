import streamlit as st
import logging
import traceback

def setup_logger():
    """로그를 설정하는 함수"""
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler("app_errors2.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    return logger


def global_exception_handler(e):
    """예외 발생 시 에러 메시지를 처리하는 함수"""
    logger = setup_logger()
    error_msg = ("오류 메시지", "".join(traceback.format_exception(type(e), e, e.__traceback__)))
    logger.error(f"Unhandled exception occurred: {error_msg}")
    st.session_state['error']=True
    st.rerun()
    
def error_page():
    st.error("예상치 못한 오류가 발생했습니다. 관리자에게 문의하세요.")
    with st.sidebar:
        if st.button("초기 화면 돌아가기", use_container_width=True):
            st.session_state.clear()
            st.rerun()
