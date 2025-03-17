import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np
from datetime import datetime, timedelta
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db_functions import setup_activity
from src.queries import GET_UI_DATA_DIFF_ACTION


def dashboard_same_time_diff_action():
    st.title("멀티 클라이언트 동시 다른 행동")
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
        activity = setup_activity(db_type="pdu")

        st.session_state["dataframes"]["save_df"] = activity.get_df(
            GET_UI_DATA_DIFF_ACTION.format(date=date_str)
        )

    df = st.session_state["dataframes"]["save_df"]
    st.title("📊 Multi-client macro analysis, different Action")
    st.info(f"{st.session_state['selected_date']} 데이터 결과 입니다.")
    st.write(
        """
        이 분석은 멀티 클라이언트 유저의 동시 행동 두번째 방향입니다. 
        기존 멀티 클라이언트 동시 사냥 중 같은 맵, 
        서버에서 사냥시 매크로 탐지 범위에서 벗어나는 한계를 극복합니다.
        - 하나의 IP에서 동시에 다른 액션을 수행하는 행위 수를 기록합니다.
        - 그 기록 횟수가 10회 이상 넘어가는 경우 의심 유저로 간주합니다.
        """
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔹 매크로 의심 유저 수", df["srcAccountID"].nunique())
    col2.metric("🔹 중복 발생 Time 수", f"{df['logtime'].nunique():,}")
    col3.metric("🔹 중복 발생 IP 수", df["ip"].nunique())
    col4.metric(
        "🔹 중복 발생 로그 수",
        f"{df.groupby(['logtime', 'ip']).size().reset_index(name='count').shape[0]:,}",
    )
    # IP별 고유 logtime 수 분석
    ip_logtime_unique = (
        df.groupby("ip")
        .agg(
            unique_logtime_count=("logtime", "nunique"),
            unique_AID_count=("srcAccountID", "nunique"),
        )
        .reset_index()
        .sort_values("unique_logtime_count", ascending=True)
        .reset_index(drop=True)
    )
    # 누적 분포도 계산
    ip_logtime_unique["cumulative"] = ip_logtime_unique["unique_logtime_count"].cumsum()
    ip_logtime_unique["cumulative"] /= ip_logtime_unique["cumulative"].iloc[-1]
    # 그래프 크기 설정
    fig, ax1 = plt.subplots(figsize=(14, 10))

    bars = ax1.bar(
        ip_logtime_unique["ip"],
        ip_logtime_unique["unique_logtime_count"],
        color="blue",
        alpha=0.7,
        label="IP별 발생 수",
    )

    # 막대 위에 값(Label) 추가
    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:,}",
            ha="center",
            va="bottom",
            fontsize=10,
            color="blue",
        )

    ax1.set_xlabel("IP", fontsize=12)
    ax1.set_ylabel("IP별 발생 수", fontsize=12, color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.set_xticks(range(len(ip_logtime_unique["ip"])))
    ax1.set_xticklabels(ip_logtime_unique["ip"], rotation=90)

    ax2 = ax1.twinx()
    ax2.plot(
        ip_logtime_unique["ip"],
        ip_logtime_unique["unique_AID_count"],
        color="green",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=5,
        label="유저 수",
    )
    ax2.set_ylabel("IP별 유저 수", fontsize=12, color="green")
    ax2.tick_params(axis="y", labelcolor="green")

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(
        ip_logtime_unique["ip"],
        ip_logtime_unique["cumulative"],
        color="red",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=5,
        label="누적 분포",
    )
    ax3.set_ylabel("누적 분포", fontsize=12, color="red")
    ax3.tick_params(axis="y", labelcolor="red")
    ax1.set_ylim(0, ip_logtime_unique["unique_logtime_count"].max() * 1.2)
    ax2.set_ylim(0, ip_logtime_unique["unique_AID_count"].max() * 1.2)
    ax3.set_ylim(0, ip_logtime_unique["cumulative"].max() * 1.2)

    # 범례 추가
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper center")
    ax3.legend(loc="upper right")

    # 제목 추가
    st.write("---")

    col1, col2 = st.columns([6, 4])
    # Streamlit에서 표시
    with col1:
        st.write("#### IP별 logtime 고유 개수 & 누적 분포도")
        st.pyplot(fig)
    with col2:
        st.write("#### 근거 데이터")
        st.dataframe(
            ip_logtime_unique.sort_values(
                "unique_logtime_count", ascending=False
            ).reset_index(drop=True),
            height=600,
        )
    st.markdown(
        """
    ##### 📊 **그래프 요약**

    - **막대그래프 (왼쪽 Y축)**: 각 IP에서 **여러 계정이 동일 시간대에 다른 액션을 취한 고유 `logtime`의 개수**를 나타냅니다. 고유 `logtime` 수가 많을수록 그 IP에서 **다양한 계정들이 동시에 활동**한 것입니다.
    - **누적 분포도 (오른쪽 Y축)**: 고유 `logtime` 수의 누적 분포를 보여주며, 대부분의 IP는 **소수의 고유 `logtime`을 기록**하고, 일부 IP는 **많은 계정들이 동시에 다양한 액션을 취하는 경향**을 보입니다.

    ##### 🕵️‍♂️ **매크로 유저 탐지**
    - **고유 `logtime` 수가 많을수록** 해당 IP에서 **여러 계정이 동시에 활동**한 경우가 많다는 의미입니다. 이는 **매크로 유저**가 여러 계정을 동시에 사용하는 특징일 수 있습니다.

    ##### 🚀 **활용**
    - **매크로 유저 탐지**: **하나의 IP에서 다수의 계정들이 동시에 다른 액션을 취하는 패턴**을 확인하여 **매크로 활동을 추적**할 수 있습니다.
    """
    )
    top_users = (
        df.groupby("srcAccountID")
        .agg(
            count=("srcAccountID", "size"),  # 중복 행동 횟수
            ip_list=(
                "ip",
                lambda x: list(x.unique()),
            ),  # 각 srcAccountID에 해당하는 IP 목록
        )
        .reset_index()
        .sort_values("count", ascending=False)
        .head(20)
    )

    # 그래프 설정
    plt.figure(figsize=(12, 6))
    # 막대 그래프 생성
    bars = plt.bar(
        top_users["srcAccountID"].astype(str),
        top_users["count"],
        color="skyblue",
        edgecolor="black",
    )

    # 각 막대 위에 값 추가
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # 막대 중앙에 텍스트 위치
            height,  # 막대의 높이 (값)
            f"{height:,}",  # 천단위 구분
            ha="center",  # 가로 중앙 정렬
            va="bottom",  # 세로 아래 정렬
            fontsize=10,
            color="blue",
        )

    # 그래프 제목과 레이블 설정
    plt.xlabel("유저 (srcAccountID)", fontsize=12)
    plt.ylabel("중복 행동 횟수", fontsize=12)

    # x축 레이블 회전
    plt.xticks(rotation=45)
    st.write("---")
    # 그래프 출력
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### 상위 20명의 유저별 중복 행동 횟수")
        st.pyplot(plt)
    with col2:
        st.write("#### 근거 데이터")
        st.dataframe(top_users.reset_index(drop=True), use_container_width=True)
