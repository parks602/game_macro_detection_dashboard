import streamlit as st
from datetime import timedelta
import plotly.express as px
import pandas as pd


def cs_show_top_sentence():
    date_selected = st.session_state["selected_date"]
    date_str = date_selected.strftime("%Y-%m-%d")
    print_date = date_selected.strftime("%Y년 %m월 %d일")
    print_pre_date = (date_selected - timedelta(days=9)).strftime("%Y년 %m월 %d일")
    st.markdown(
        f"#### {print_pre_date} 부터 {print_date}까지 10일간의 데이터 통계입니다."
    )
    return date_str


def cs_show_block_warning(block_ratio, block_percentage):
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


def cs_display_metrics(
    all_user_count, clean_user, block_user, suspic_user, macro_user, new_detected_users
):
    col0, col1, col2 = st.columns(3)
    col0.metric(label="📌 전체 분석 유저 수", value=f"{all_user_count:,}")
    col1.metric(label="📌 클린 유저 수", value=f"{clean_user:,}")
    col2.metric(label="📌 블럭 유저 수", value=f"{block_user}")
    st.write("---")
    col0, col1, col2 = st.columns(3)
    col0.metric(label="📌 매크로 의심 유저 수", value=f"{suspic_user}")
    col1.metric(label="📌 매크로 탐지 유저 수", value=f"{macro_user}")
    col2.metric(label="📌 지정 일자 신규 탐지 유저 수", value=f"{new_detected_users}")
    st.write("---")


def cs_display_pie_charts(macro_user, suspic_user, block_user, clean_user):
    # 1. 전체 유저 분포 (정상, 매크로, 의심, 블럭)
    pie_data1 = pd.DataFrame(
        {
            "유저 유형": [
                "클린 유저",
                "매크로 탐지 유저",
                "매크로 의심 유저",
                "블럭 유저",
            ],
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
