import streamlit as st
from datetime import datetime, timedelta
import sys, os
import plotly.express as px
import pandas as pd
import time
from ui_utils import configure_streamlit

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db_functions import setup_activity
from src.queries import (
    GET_DAILY_SUMMARY_DATA,
)


def dashboard_summary():

    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = datetime.now().date() - timedelta(days=1)
    if "dataframes" not in st.session_state:
        st.session_state["dataframes"] = {}
    # 📌 서머리 섹션
    st.title("🕵️ 매크로 탐지 대시보드")
    # 탐지 기법 요약 섹션 (이전 코드와 연결)
    st.markdown("### 📖 탐지 기법 소개")
    st.write(
        "아래의 4가지 방법을 통해 매크로 유저를 의심합니다. 아래 4가지 방법 중 3가지 이상 의심된 유저를 매크로로 탐지합니다."
    )

    with st.expander("1️⃣ 멀티 클라이언트 동시 같은 액션"):
        st.write(
            """
            ##### 하나의 IP에서 동시에 같은 액션을 수행하는 여러 개의 계정 검출
            ###### 전체 행동(Action = 1) 중 50% 이상이 아래 조건을 만족하는 다른 유저가 존재할 경우 매크로 의심
            - 같은 IP
            - 다른 AID
            - 다른 서버 또는 맵 (파티 사냥 방지)
            - 같은 시간
            - 같은 Action(1)
            """
        )

    with st.expander("2️⃣ 멀티 클라이언트 동시 다른 액션"):
        st.write(
            """
            ##### 하나의 IP에서 동시에 다른 행동을 수행하는 계정 검출
            ###### 전체 행동(ALL Action) 중 아래 조건을 만족하는 다른 유저가 존재할 경우 매크로 의심
            - 같은 IP
            - 다른 AID
            - 같은 시간
            - 다른 ACTION
            """
        )

    with st.expander("3️⃣ 유저간 행동 유사성 기반"):
        st.write(
            """
            ##### 유저 간 행동의 코사인 유사도가 99% 이상인 계정 검출
            ###### 하나의 매크로 프로그램을 여러 계정에 적용한 경우, 유사한 행동 패턴을 보일 것으로 가정
            - 유저 간 24시간 동안의 플레이 시간에 대해 1분 단위로 코사인 유사도 측정
            - 유사도 99% 이상인 그룹 중, 그룹 내 유저 수가 2명 이상이면 매크로 의심
            """
        )

    with st.expander("4️⃣ 유저별 자기 유사도 기반"):
        st.write(
            """
            ##### 자기 행동의 코사인 유사도가 97% 이상인 계정 검출
            ###### 매크로 유저는 반복적인 행동 사이클을 유지하기 때문에 자기 유사도가 높을 것으로 가정
            - 유저 개인의 1분 단위 액션 벡터를 생성한 후 유사도 측정
            - 자기 유사도 97% 이상이면 매크로 의심
            """
        )

    st.markdown("### 🔥 탐지 현황 요약")
    date_selected = st.date_input(
        "분석 날짜를 선택하세요", value=st.session_state["selected_date"]
    )

    yesterday = datetime.today().date() - timedelta(days=1)
    current_time = datetime.now().time()
    if date_selected != st.session_state["selected_date"]:
        st.session_state["selected_date"] = date_selected
        st.session_state["last_active"] = time.time()
        if date_selected < datetime.strptime("2025-03-09", "%Y-%m-%d").date():
            st.error(
                "2025년 3월 9일 부터 선택 가능합니다. 그제 날짜 데이터가 출력됩니다."
            )
            time.sleep(3)
            st.session_state["selected_date"] = datetime.now().date() - timedelta(
                days=2
            )
        elif date_selected == yesterday and current_time.hour < 15:
            st.error(
                "오우 아직 데이터가 준비 되지 않았어요... 오후 3시에 업데이트 됩니다. 그제 날짜로 돌아갑니다."
            )
            time.sleep(3)
            st.session_state["selected_date"] = datetime.now().date() - timedelta(
                days=2
            )
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
    try:
        st.session_state["dataframes"]["save_df"] = activity.get_df(
            GET_DAILY_SUMMARY_DATA.format(date=date_str)
        )
    except Exception as e:
        st.error("데이터를 불러오는 중 오류가 발생했습니다.")
        return
    finally:
        activity.disconnect_from_db()
    df = st.session_state["dataframes"]["save_df"]

    # df = pd.read_csv("C:/Users/Gravity/Desktop/test.csv")
    # 10일간 매크로 User, 블럭된 유저, 의심 User 수 계산
    summary_counts = (
        df.groupby("distinction")["AID"]
        .nunique()
        .rename(
            {
                "detection": "매크로 탐지 유저",
                "suspicion": "매크로 의심 유저",
                "normal": "클린 유저",
                "block": "블럭된 유저",
            }
        )
    )
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

    macro_count = summary_counts.get("매크로 탐지 유저", 0)
    suspicion_count = summary_counts.get("매크로 의심 유저", 0)
    block_aid = df[(df["Date"] == date_str) & (df["distinction"] == "block")][
        "AID"
    ].unique()
    block_count = df[
        (df["distinction"] == "detection") & (df["AID"].isin(block_aid))
    ].shape[0]
    normal_count = summary_counts.get("클린 유저", 0)
    # 📊 주요 지표 4개를 한 줄에 배치
    st.subheader("유저 분석 분포")
    col0, col1, col2, col3 = st.columns(4)
    col0.metric(
        label="📌 클린 유저 수",
        value=f"{normal_count:,}",
    )
    col1.metric(
        label="📌 매크로 탐지 유저 수",
        value=f"{macro_count:,}",
    )
    col2.metric(
        label="📌 매크로 의심 유저 수",
        value=f"{suspicion_count}",
    )
    col3.metric(
        label="📌 현재 블럭 유저 수",
        value=f"{block_count}",
    )
    st.write("---")
    st.subheader("매크로 의심 유저 분포")
    col4, col5, col6, col7 = st.columns(4)
    col4.metric(
        label="1️⃣ 멀티 클라이언트 동시 같은 액션",
        value=len(df[df["reason"] == "action_one"]["AID"].unique()),
    )
    col5.metric(
        label="2️⃣ 멀티 클라이언트 동시 다른 액션",
        value=len(df[df["reason"] == "action_diff"]["AID"].unique()),
    )
    col6.metric(
        label="3️⃣ 유저간 행동 유사성 기반",
        value=len(df[df["reason"] == "cosine_sim"]["AID"].unique()),
    )
    col7.metric(
        label="4️⃣ 유저별 자기 유사도 기반",
        value=len(df[df["reason"] == "self_sim"]["AID"].unique()),
    )

    st.markdown("---")

    st.subheader("10일간 탐지된 유저 현황")

    # Pie Chart 데이터 준비

    # 1. 전체 유저 분포 (정상, 매크로, 의심, 블럭)
    pie_data1 = pd.DataFrame(
        {
            "유저 유형": ["정상 유저", "매크로 유저", "의심 유저", "블럭 유저"],
            "수": [normal_count, macro_count, suspicion_count, block_count],
        }
    )
    fig1 = px.pie(pie_data1, names="유저 유형", values="수", title="🔍 전체 유저 비율")
    fig1.update_traces(textinfo="value+percent")

    # 2. 매크로 탐지 유저 vs 블럭된 유저
    pie_data2 = pd.DataFrame(
        {
            "유저 유형": ["매크로 탐지 유저", "블럭된 유저"],
            "수": [macro_count, block_count],
        }
    )
    fig2 = px.pie(
        pie_data2, names="유저 유형", values="수", title="🔍 매크로 탐지 vs 블럭된 유저"
    )
    fig2.update_traces(textinfo="value+percent")

    # 3. 매크로 탐지 유저 vs 신규 검출 유저
    pie_data3 = pd.DataFrame(
        {
            "유저 유형": ["매크로 탐지 유저", "신규 검출 유저"],
            "수": [macro_count, new_detected_users],
        }
    )
    fig3 = px.pie(
        pie_data3,
        names="유저 유형",
        values="수",
        title="🔍 매크로 탐지 vs 신규 검출 유저",
    )
    fig3.update_traces(textinfo="value+percent")

    # 4. 매크로 탐지 유저 vs 매크로 의심 유저
    pie_data4 = pd.DataFrame(
        {
            "유저 유형": ["매크로 탐지 유저", "매크로 의심 유저"],
            "수": [macro_count, suspicion_count],
        }
    )
    fig4 = px.pie(
        pie_data4,
        names="유저 유형",
        values="수",
        title="🔍 매크로 탐지 vs 매크로 의심 유저",
    )
    fig4.update_traces(textinfo="value+percent")

    # 5. 매크로 탐지 유저 중 reason 1 vs reason 2
    reason_1_count = len(df[df["reason"] == "action_one"]["AID"].unique())
    reason_2_count = len(df[df["reason"] == "action_diff"]["AID"].unique())
    reason_3_count = len(df[df["reason"] == "cosine_sim"]["AID"].unique())
    reason_4_count = len(df[df["reason"] == "self_sim"]["AID"].unique())

    pie_data5 = pd.DataFrame(
        {
            "유저 유형": [
                "멀티 클라이언트 동시 같은 액션",
                "멀티 클라이언트 동시 다른 액션",
                "유저간 행동 유사성 기반",
                "유저별 자기 유사도 기반",
            ],
            "수": [reason_1_count, reason_2_count, reason_3_count, reason_4_count],
        }
    )

    fig5 = px.pie(
        pie_data5,
        names="유저 유형",
        values="수",
        title="🔍 매크로 탐지 유저 분포",
    )
    fig5.update_traces(textinfo="value+percent")

    # Streamlit에 차트 표시
    st.subheader("📊 유저 유형 분석 (매크로 탐지율)")
    col99, blank0, col98 = st.columns([3, 1, 6])
    with col99:
        st.plotly_chart(fig1)
    with col98:
        # 전체 유저 비율 계산
        total_users = normal_count + macro_count + suspicion_count + block_count
        suspicion_ratio = (suspicion_count / total_users) * 100
        macro_ratio = (macro_count / total_users) * 100
        block_ratio = (block_count / total_users) * 100

        if suspicion_ratio >= 10:
            suspicion_message = f"의심 유저 비율이 **{suspicion_ratio:.2f}**%로 10% 이상으로 나타났습니다. 경고가 필요합니다."
            st.error(suspicion_message)  # 에러로 표시
        elif suspicion_ratio >= 3:
            suspicion_message = f"의심 유저 비율이 **{suspicion_ratio:.2f}**%로 3%에서 10% 사이로 유지되고 있습니다. 주의가 필요합니다."
            st.info(suspicion_message)  # 정보로 표시
        else:
            suspicion_message = f"의심 유저 비율이 **{suspicion_ratio:.2f}**%로 3% 이하로 비교적 낮은 수준입니다."
            st.success(suspicion_message)  # 성공으로 표시

        # 매크로 유저와 블럭 유저 비율 비교 설명
        if macro_ratio > block_ratio:
            macro_message = f"매크로 유저 비율이 **{macro_ratio:.2f}**%로 블럭 유저보다 더 많습니다. 매크로 유저 제재가 필요합니다."
            st.error(macro_message)  # 에러로 표시
        elif macro_ratio <= block_ratio:
            macro_message = f"매크로 유저 비율이 **{macro_ratio:.2f}**%로 블럭 유저보다 적습니다. 현재 상태는 매크로 유저 관리가 중간 단계로 볼 수 있습니다."
            st.info(macro_message)  # 성공으로 표시
        elif macro_ratio == 0:
            macro_message = f"매크로 유저 비율이 **{macro_ratio:.2f}**%로 현재 탐지된 매크로 유저를 모두 제재한 상태입니다.."
            st.success(macro_message)  # 성공으로 표시

        # 매크로 유저의 심각성 수준
        if macro_ratio < 0.25:
            severity_message = f"매크로 유저 비율이 **{macro_ratio:.2f}**%로 0.25% 미만입니다. 이는 낮은 수준으로 큰 문제는 아닙니다."
            st.success(severity_message)  # 성공으로 표시
        elif macro_ratio < 0.5:
            severity_message = f"매크로 유저 비율이 **{macro_ratio:.2f}**%로 0.25%에서 0.5% 사이입니다. 경계가 필요한 수준입니다."
            st.info(severity_message)  # 정보로 표시
        else:
            severity_message = f"매크로 유저 비율이 **{macro_ratio:.2f}**%로 0.5% 이상입니다. 이는 심각한 수준으로, 즉각적인 조치가 필요합니다."
            st.error(severity_message)  # 에러로 표시
        # 결과 출력
        st.subheader("📊 전체 유저 분석 결과")
        st.markdown(
            f"""
        - **의심 유저 비율**: {suspicion_message}
        - **매크로 유저 비율 vs 블럭 유저 비율**: {macro_message}
        - **매크로 유저 심각성**: {severity_message}
        """
        )
    st.write("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.subheader("📊 매크로 탐지 vs 블럭된 유저")
        st.plotly_chart(fig2)
    with col2:
        st.subheader("📊 매크로 탐지 vs 신규 검출 유저")
        st.plotly_chart(fig3)
    with col3:
        st.subheader("📊 매크로 탐지 vs 매크로 의심 유저")
        st.plotly_chart(fig4)
    st.write("---")
    col4, blank0, col5 = st.columns([4, 1, 5])
    with col4:
        st.subheader("매크로 의심 유저 유형 분포")

        st.plotly_chart(fig5)

    # 기존 계산된 값 사용
    reason_counts = {
        "멀티 클라이언트 동시 같은 액션": reason_1_count,
        "멀티 클라이언트 동시 다른 액션": reason_2_count,
        "유저 간 행동 유사성": reason_3_count,
        "유저별 자기 유사도": reason_4_count,
    }

    # 전체 매크로 의심 유저 수
    total_suspects = sum(reason_counts.values())

    # 가장 많은 비율을 차지하는 유형 찾기
    max_reason = max(reason_counts, key=reason_counts.get)
    max_percentage = (
        (reason_counts[max_reason] / total_suspects) * 100 if total_suspects > 0 else 0
    )

    # 각 이유별 비율 계산
    reason_percentages = {
        reason: (count / total_suspects) * 100 if total_suspects > 0 else 0
        for reason, count in reason_counts.items()
    }

    with col5:
        # 📌 Streamlit UI
        st.markdown("### 매크로 의심 통계 요약")

        st.markdown(
            f"현재 매크로 의심 유저 중 가장 많은 비율을 차지하는 것은 **{max_reason}**이며, 전체 의심 유저 중 **{max_percentage:.1f}**%를 차지하고 있습니다."
        )

        st.markdown("#### 📊 매크로 의심 유형별 비율")
        st.write(
            f"""
        - **멀티 클라이언트 동시 같은 액션**: {reason_percentages["멀티 클라이언트 동시 같은 액션"]:.1f}%
        - **멀티 클라이언트 동시 다른 액션**: {reason_percentages["멀티 클라이언트 동시 다른 액션"]:.1f}%
        - **유저 간 행동 유사성**: {reason_percentages["유저 간 행동 유사성"]:.1f}%
        - **유저별 자기 유사도**: {reason_percentages["유저별 자기 유사도"]:.1f}%
        """
        )

        st.markdown("#### 📈 분석 결과 해석")
        st.write(
            """
        이 데이터는 특정 시간대에 동일한 IP에서 여러 개의 클라이언트를 사용하는 패턴이 얼마나 자주 발생하는지를 보여줍니다.  
        또한, 유저 간 행동 유사도가 높은 그룹이 다수 발견되었다면, 특정 자동화된 행동 패턴이 존재할 가능성이 큽니다.  
        자기 유사도가 높은 유저의 경우, 오랜 시간 동안 동일한 패턴으로 행동한 것으로 판단되며, 반복적인 자동화 플레이가 의심됩니다.

        이 분석을 통해, 특정 매크로 유형이 게임 내에서 얼마나 많은 영향을 미치는지 파악할 수 있으며,  
        이를 기반으로 보다 정교한 필터링 및 대응 방안을 마련할 수 있습니다.
        """
        )


# main.py
import subprocess

if __name__ == "__main__":
    configure_streamlit()
    dashboard_summary()
