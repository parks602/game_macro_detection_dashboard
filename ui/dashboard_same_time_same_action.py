import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np
from datetime import datetime, timedelta
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db_functions import setup_activity
from src.queries import GET_MULTI_CHAR_USER_DATA


def dashboard_same_time_same_action():
    st.title("멀티 클라이언트 동시 같은 행동")
    plt.rc("font", family="Malgun Gothic")

    with st.sidebar:
        if st.button("시간연장"):
            st.session_state["last_active"] = time.time()
            st.success("세션 연장 완료")

    # Session State에서 날짜 저장 및 불러오기
    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = datetime.now().date() - timedelta(days=1)
    if "dataframes" not in st.session_state:
        st.session_state["dataframes"] = {}

    # 날짜 입력 위젯
    date_selected = st.date_input(
        "날짜를 선택하세요", value=st.session_state["selected_date"]
    )
    current_time = datetime.now().time()

    yesterday_date = datetime.today().date() - timedelta(days=1)
    analysis_date = datetime.now().date() - timedelta(days=2)
    if date_selected != st.session_state["selected_date"]:
        st.session_state["last_active"] = time.time()
        if date_selected < datetime.strptime("2025-03-09", "%Y-%m-%d").date():
            st.error(
                f"2025년 3월 9일 부터 선택 가능합니다. {analysis_date} 날짜 데이터가 출력됩니다."
            )
            time.sleep(3)
            st.session_state["selected_date"] = analysis_date
        elif (date_selected == yesterday_date and current_time.hour < 15) or (
            date_selected > yesterday_date
        ):
            st.error(
                f"오우 아직 {date_selected} 데이터가 준비 되지 않았어요... 오후 3시에 업데이트 됩니다. {analysis_date} 날짜로 돌아갑니다."
            )
            time.sleep(3)
            st.session_state["selected_date"] = analysis_date
        else:
            st.session_state["selected_date"] = date_selected
            st.success(f"선택한 날짜 : {date_selected}")
            st.rerun()
    if (
        st.session_state["selected_date"]
        >= datetime.strptime("2025-02-25", "%Y-%m-%d").date()
    ):
        # 파일 경로 생성
        date_str = st.session_state["selected_date"].strftime("%Y-%m-%d")
        activity = setup_activity(db_type="datamining")

        try:
            st.session_state["dataframes"]["save_df"] = activity.get_df(
                GET_MULTI_CHAR_USER_DATA.format(date=date_str)
            )
        except Exception as e:
            st.error("데이터를 불러오는 중 오류가 발생했습니다.")
            return
        finally:
            activity.disconnect_from_db()

    df = st.session_state["dataframes"]["save_df"]
    st.title("📊 Multi-client macro analysis, same Action")
    st.info(f"{st.session_state['selected_date']} 데이터 결과 입니다.")
    st.write(
        """
        이 분석은 멀티 클라이언트 유저의 동시 행동 첫번째 방향입니다. 
        기존 멀티 클라이언트 동시 사냥 중 다른 맵, 
        서버에서 사냥시 매크로 유저로 탐지합니다.
        - 하나의 IP에서 동시에 줍기 액션을 수행하는 행위 수를 기록합니다.
        - 전체 줍기 횟수가 1000회 이상, 중복율이 50%가 넘어가는 경우 의심 유저로 간주합니다.
        """
    )
    macro_df = df[
        (df["Total_action_count"] >= 1000) & (df["Overlap_percentage"] > 50)
    ].reset_index(drop=True)
    action_mean = round(macro_df["Total_action_count"].mean())
    duple_mean = round(macro_df["Overlap_count"].mean())
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🔹 매크로 의심 유저 수", macro_df["AID"].nunique())
    col2.metric("🔹 중복 IP 수", macro_df["IP"].nunique())
    col3.metric("🔹 중복 IP 수 접속 유저 수", df["AID"].nunique())
    col4.metric("🔹 매크로 의심 유저 평균 액션 수", action_mean)
    col5.metric("🔹 매크로 의심 유저 평균 중복 액션 수", duple_mean)

    aid_count = (
        df.groupby("IP")["AID"]
        .nunique()
        .reset_index()
        .rename(columns={"AID": "AID_count"})
    )
    agg_df = (
        df.groupby("IP")[["Overlap_count", "Total_action_count"]].mean().reset_index()
    )

    result_df = df.merge(aid_count, on="IP").merge(
        agg_df, on="IP", suffixes=("", "_mean")
    )
    result_df[["Overlap_count_mean", "Total_action_count_mean"]] = result_df[
        ["Overlap_count_mean", "Total_action_count_mean"]
    ].round(1)
    result_df = (
        result_df[["IP", "AID_count", "Overlap_count_mean", "Total_action_count_mean"]]
        .drop_duplicates()
        .sort_values("AID_count", ascending=False)
        .reset_index(drop=True)
    )
    st.write("---")
    st.write("##### 전체 IP별 줍기 행위 통계")
    st.dataframe(result_df, use_container_width=True)

    df["IP_total"] = df.groupby("IP")["Total_action_count"].transform("sum")
    df = df.sort_values(
        by=["IP_total", "Total_action_count"], ascending=[False, False]
    ).reset_index(drop=True)
    df.drop(columns=["IP_total"], inplace=True)
    st.write("##### 의심 유저 도출 근거 데이터")
    st.dataframe(
        df[["AID", "IP", "Overlap_count", "Total_action_count", "Overlap_percentage"]],
        use_container_width=True,
    )
