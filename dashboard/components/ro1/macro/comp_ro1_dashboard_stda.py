import streamlit as st
import matplotlib.pyplot as plt


def stda_show_top_sentence():
    date_selected = st.session_state["selected_date"]
    date_str = date_selected.strftime("%Y-%m-%d")
    print_date = date_selected.strftime("%Y년 %m월 %d일")
    st.info(f"{print_date} 데이터 결과 입니다.")
    st.write(
        """
        이 분석은 멀티 클라이언트 유저의 동시 행동 두번째 방향입니다. 
        기존 멀티 클라이언트 동시 사냥 중 같은 맵, 
        서버에서 사냥시 매크로 탐지 범위에서 벗어나는 한계를 극복합니다.
        - 하나의 IP에서 동시에 다른 액션을 수행하는 행위 수를 기록합니다.
        - 그 기록 횟수가 10회 이상 넘어가는 경우 의심 유저로 간주합니다.
        """
    )
    return date_str


def stda_show_metrics(df):
    """대시보드 핵심 지표 출력"""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔹 매크로 의심 유저 수", df["srcAccountID"].nunique())
    col2.metric("🔹 중복 발생 Time 수", f"{df['logtime'].nunique():,}")
    col3.metric("🔹 중복 발생 IP 수", df["ip"].nunique())
    col4.metric(
        "🔹 중복 발생 로그 수",
        f"{df.groupby(['logtime', 'ip']).size().reset_index(name='count').shape[0]:,}",
    )


def stda_show_graph_logtime(fig):
    st.write("#### IP별 logtime 고유 개수 & 누적 분포도")
    st.pyplot(fig)


def stda_show_df_logtime(ip_logtime_unique):
    st.write("#### 근거 데이터")
    st.dataframe(
        ip_logtime_unique.sort_values(
            "unique_logtime_count", ascending=False
        ).reset_index(drop=True),
        height=600,
    )


def stda_show_graph_summary():
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


def stda_show_graph_top_users(plt):
    st.write("#### 상위 20명의 유저별 중복 행동 횟수")
    st.pyplot(plt)


def stda_show_dataframe_top_user(top_users):
    st.write("#### 근거 데이터")
    st.dataframe(top_users.reset_index(drop=True), use_container_width=True)
