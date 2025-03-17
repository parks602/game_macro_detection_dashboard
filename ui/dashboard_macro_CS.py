import streamlit as st
from datetime import datetime, timedelta
import sys, os
import plotly.express as px
import pandas as pd
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ui_utils import configure_streamlit

from src.db_functions import setup_activity
from src.queries import (
    GET_DAILY_SUMMARY_DATA,
)


def dashboard_CS():
    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = datetime.now().date() - timedelta(days=2)
    if "dataframes" not in st.session_state:
        st.session_state["dataframes"] = {}
    # 📌 서머리 섹션
    st.title("RO1 바포메트 서버 유저 현황")
    date_selected = st.date_input(
        "분석 날짜를 선택하세요", value=st.session_state["selected_date"]
    )
    current_time = datetime.now().time()
    yesterday_date = datetime.today().date()-timedelta(days=1)
    analysis_date = datetime.now().date() - timedelta(days=2)
    
    if date_selected != st.session_state["selected_date"]:
        st.session_state["selected_date"] = date_selected
        st.session_state["last_active"] = time.time()
        if date_selected < datetime.strptime("2025-03-09", "%Y-%m-%d").date():
            st.error(
                f"2025년 3월 9일 부터 선택 가능합니다. {analysis_date} 날짜 데이터가 출력됩니다."
            )
            time.sleep(3)
            st.session_state["selected_date"] = analysis_date
        elif (date_selected == yesterday_date and current_time.hour < 15) or (date_selected > yesterday_date):
            st.error(
                f"오우 아직 {date_selected} 데이터가 준비 되지 않았어요... 오후 3시에 업데이트 됩니다. {analysis_date} 날짜로 돌아갑니다."
            )
            time.sleep(3)
            st.session_state["selected_date"] = analysis_date
        else:
            st.session_state["selected_date"] = date_selected
            st.success(f"선택한 날짜 : {date_selected}")
            st.rerun()

    date_str = st.session_state["selected_date"].strftime("%Y-%m-%d")
    print_date = st.session_state["selected_date"].strftime("%Y년 %m월 %d일")
    print_pre_date = (st.session_state["selected_date"] - timedelta(days=9)).strftime(
        "%Y년 %m월 %d일"
    )
    st.markdown(
        f"#### {print_pre_date} 부터 {print_date}까지 10일간의 데이터 통계입니다."
    )

    activity = setup_activity(db_type="pdu")
    st.session_state["dataframes"]["save_df"] = activity.get_df(
        GET_DAILY_SUMMARY_DATA.format(date=date_str)
    )
    df = st.session_state["dataframes"]["save_df"]
    # 오늘 날짜에 해당하는 신규 검출 유저 수 계산
    target_aids = df[(df["Date"] == date_str) & (df["distinction"] == "detection")][
        "AID"
    ]

    # 다른 날짜에서 "distinction" == "detection" 인 AID 목록
    other_aids = df[(df["Date"] != date_str) & (df["distinction"] == "detection")][
        "AID"
    ]
    # 다른 날짜에 없는 AID만 필터링
    unique_aids = target_aids[~target_aids.isin(other_aids)]

    # 고유한 AID 개수 출력
    new_detected_users = unique_aids.nunique()

    all_user_count = df["AID"].nunique()
    macro_user = df[df["distinction"] == "detection"]["AID"].nunique()
    suspic_user = df[df["distinction"] == "suspicion"]["AID"].nunique()
    block_aids = df[(df["Date"] == date_str) & (df["distinction"] == "block")][
        "AID"
    ].unique()
    block_user = df[
        (df["distinction"] == "detection") & (df["AID"].isin(block_aids))
    ].shape[0]
    clean_user = all_user_count - macro_user - suspic_user - block_user
    block_ratio = round(block_user / macro_user, 2)
    block_percentage = round(block_ratio * 100, 2)

    if block_ratio < 0.5:
        st.error(
            f"매크로 제재 비율 : {block_percentage}%, 당장 매크로 유저 제재가 필요합니다. 신속한 매크로 유저 제재가 필요합니다."
        )
    elif block_ratio < 0.7:
        st.error(
            f"매크로 제재 비율 : {block_percentage}%, 여전히 제재율이 낮습니다. 신속한 매크로 유저 제재가 필요합니다."
        )
    elif block_ratio < 0.9:
        st.info(
            f"매크로 제재 비율 : {block_percentage}%, 매크로 유저 제재가 이루어 지고 있습니다. 나머지 매크로 유저도 제재가 필요합니다."
        )
    elif block_ratio == 0:
        st.success(
            f"매크로 제재 비율 : {block_percentage}%, 현재 제재가 필요한 매크로 유저가 없습니다."
        )
    col0, col1, col2 = st.columns(3)
    col0.metric(
        label="📌 전체 분석 유저 수",
        value=f"{all_user_count:,}",
    )
    col1.metric(
        label="📌 클린 유저 수",
        value=f"{clean_user:,}",
    )
    col2.metric(
        label="📌 블럭 유저 수",
        value=f"{block_user}",
    )
    st.write("---")
    col0, col1, col2 = st.columns(3)
    col0.metric(
        label="📌 매크로 의심 유저 수",
        value=f"{suspic_user}",
    )
    col1.metric(
        label="📌 매크로 탐지 유저 수",
        value=f"{macro_user}",
    )
    col2.metric(
        label="📌 지정 일자 신규 탐지 유저 수",
        value=f"{new_detected_users}",
    )
    st.write("---")

    # 1. 전체 유저 분포 (정상, 매크로, 의심, 블럭)
    pie_data1 = pd.DataFrame(
        {
            "유저 유형": ["클린 유저", "매크로 탐지 유저", "매크로 의심 유저", "블럭 유저"],
            "수": [clean_user, macro_user, suspic_user, block_user],
        }
    )
    fig1 = px.pie(pie_data1, names="유저 유형", values="수", title="🔍 전체 유저 비율")
    fig1.update_traces(textinfo="value+percent")

    # 2. 매크로 탐지 유저 vs 블럭된 유저
    pie_data2 = pd.DataFrame(
        {
            "유저 유형": ["매크로 탐지 유저", "블럭된 유저"],
            "수": [macro_user, block_user],
        }
    )
    fig2 = px.pie(
        pie_data2, names="유저 유형", values="수", title="🔍 매크로 탐지 vs 블럭 유저"
    )
    fig2.update_traces(textinfo="value+percent")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 전체 유저 유형 분포")
        st.plotly_chart(fig1)
    with col2:
        st.subheader("📊 매크로 탐지 vs 블럭 유저")
        st.plotly_chart(fig2)
