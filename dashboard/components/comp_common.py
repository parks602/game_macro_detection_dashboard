import streamlit as st
from datetime import datetime, timedelta
import time


def date_selector():
    date_selected = st.date_input(
        "분석 날짜를 선택하세요", value=st.session_state["selected_date"]
    )
    current_time = datetime.now().time()
    yesterday_date = datetime.today().date() - timedelta(days=1)
    if date_selected != st.session_state["selected_date"]:
        if (date_selected > yesterday_date) or (
            date_selected == yesterday_date and current_time.hour < 15
        ):
            st.error(
                f"아직 {date_selected} 데이터가 준비 되지 않았습니다. 오후 3시에 업데이트 됩니다."
            )
            time.sleep(2)
            date_selected = st.session_state["selected_date"]
            st.rerun()
        else:
            st.session_state["selected_date"] = date_selected
            st.rerun()
