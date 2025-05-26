import streamlit as st
import logging
import traceback
import os
from datetime import datetime


def setup_logger():
    """로그를 설정하는 함수"""
    logger = logging.getLogger(__name__)
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logger')
    os.makedirs(log_dir, exist_ok = True)
    today_str = datetime.now().strftime("%Y-%m%d")
    log_filename = os.path.join(log_dir, f'{today_str}_apperror.log')
    handler = logging.FileHandler(log_filename)
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
    st.stop()
    
def error_page():
    st.error("예상치 못한 오류가 발생했습니다. 관리자에게 문의하세요.")
    with st.sidebar:
        if st.button("초기 화면 돌아가기", use_container_width=True):
            st.session_state.clear()
            st.rerun()
