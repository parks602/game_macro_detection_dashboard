import streamlit as st


def stsa_show_top_sentence():
    date_selected = st.session_state["selected_date"]
    date_str = date_selected.strftime("%Y-%m-%d")
    print_date = date_selected.strftime("%Y년 %m월 %d일")
    st.info(f"{print_date} 데이터 결과 입니다.")
    st.write(
        """
        이 분석은 멀티 클라이언트 유저의 동시 행동 첫번째 방향입니다. 
        기존 멀티 클라이언트 동시 사냥 중 다른 맵, 
        서버에서 사냥시 매크로 유저로 탐지합니다.
        - 하나의 IP에서 동시에 줍기 액션을 수행하는 행위 수를 기록합니다.
        - 전체 줍기 횟수가 1000회 이상, 중복율이 50%가 넘어가는 경우 의심 유저로 간주합니다.
        """
    )
    return date_str


def stsa_show_metrics(stats):
    """대시보드 핵심 지표 출력"""
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🔹 매크로 의심 유저 수", stats["macro_users"])
    col2.metric("🔹 중복 IP 수", stats["unique_ips"])
    col3.metric("🔹 중복 IP 수 접속 유저 수", stats["total_users"])
    col4.metric("🔹 매크로 의심 유저 평균 액션 수", stats["avg_actions"])
    col5.metric("🔹 매크로 의심 유저 평균 중복 액션 수", stats["avg_overlap"])


def stsa_show_dataframes(result_df, df):
    """데이터 프레임 출력"""
    st.write("---")
    st.write("##### 전체 IP별 줍기 행위 통계")
    st.dataframe(result_df, use_container_width=True)

    st.write("##### 의심 유저 도출 근거 데이터")
    st.dataframe(
        df[["AID", "IP", "Overlap_count", "Total_action_count", "Overlap_percentage"]],
        use_container_width=True,
    )
