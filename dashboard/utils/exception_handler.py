import streamlit as st
import logging
import sys
import traceback


def setup_logger():
    """로그를 설정하는 함수"""
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler("app_errors.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    return logger


def global_exception_handler(error_msg):
    """예외 발생 시 에러 메시지를 처리하는 함수"""
    logger = setup_logger()
    logger.error(f"Unhandled exception occurred: {error_msg}")

    # 사용자에게 알림 메시지 표시
    st.error("예상치 못한 오류가 발생했습니다. 관리자에게 문의하세요.")
    st.error(f"예상치 못한 오류가 발생했습니다.\n\n{error_msg}")
    st.stop()


def configure_exception_handler():
    """전역 예외 핸들러 설정"""
    sys.excepthook = lambda etype, e, tb: global_exception_handler(
        "".join(traceback.format_exception(etype, e, tb))
    )
