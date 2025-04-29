import streamlit as st
from datetime import timedelta


def summary_show_top_sentence():
    date_selected = st.session_state["selected_date"]
    date_str = date_selected.strftime("%Y-%m-%d")
    print_date = st.session_state["selected_date"].strftime("%Y년 %m월 %d일")
    print_pre_date = (st.session_state["selected_date"] - timedelta(days=9)).strftime(
        "%Y년 %m월 %d일"
    )
    st.markdown(
        f"#### {print_pre_date} 부터 {print_date}까지 10일간의 데이터 통계입니다."
    )
    return date_str


def summary_show_expanders():
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


def summary_show_first_metric(normal_count, macro_count, suspicion_count, block_count):
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


def summary_show_second_metric(df):
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


def summary_show_explain(normal_count, macro_count, suspicion_count, block_count):
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


def summary_show_bottom(reason_counts):
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
