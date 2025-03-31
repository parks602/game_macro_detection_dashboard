import streamlit as st
from datetime import datetime, timedelta
import os
import sys
from components.ro1.macro.comp_ro1_dashboard import (
    dashboard_CS,
    dashboard_user_detail,
    dashboard_summary,
    dashboard_same_time_same_action,
    dashboard_same_time_diff_action,
    dashboard_cos_sim,
    dashboard_self_sim,
)


def ro1_macro_dashbaord(
    dashboard_options: list = [
        "RO1 매크로 현황",
        "유저 세부 사항",
        "0. 대시보드 요약",
        "1. 멀티 클라이언트-(같은행위)",
        "2. 멀티 클라이언트-(다른행위)",
        "3. 코사인 유사도",
        "4. 자기 유사도",
    ]
):
    if "selected_date" not in st.session_state:
        now = datetime.now()
        # 현재 시간이 15시 이상이면 1일 전, 아니면 2일 전
        if now.hour >= 15:
            st.session_state["selected_date"] = now.date() - timedelta(days=1)
        else:
            st.session_state["selected_date"] = now.date() - timedelta(days=2)

    with st.sidebar:
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
