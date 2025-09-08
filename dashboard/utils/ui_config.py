import streamlit as st
import os
from dotenv import load_dotenv
import secrets


def configure_streamlit():
    st.set_page_config(
        page_title="Gravity DashBoard",
        page_icon="asset//icon/gravity.ico",
        layout="wide",
    )

    st.markdown(
        """
            <style>
                   .block-container {
                        padding-top: 2rem;
                        padding-bottom: 1rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
            <style>
                .big-font {
                    font-size:25px !important;
                }
            </style>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <style>
        /* 우측 상단 점 3개 메뉴 숨기기 */
        .css-1lcbm6t {
            visibility: hidden;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


# .env 파일 로드
load_dotenv()


class Config:
    # JWT 설정
    JWT_SECRET = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", 24))

    # 쿠키 설정
    COOKIE_NAME = "gravity_auth_token"
    COOKIE_SECURE = True  # HTTPS 환경에서만 사용
    COOKIE_HTTPONLY = False  # JavaScript에서 접근 불가 (보안 강화)
