import streamlit as st


def self_show_top_sentence():
    date_selected = st.session_state["selected_date"]
    date_str = date_selected.strftime("%Y-%m-%d")

    print_date = date_selected.strftime("%Y년 %m월 %d일")
    st.info(f"{print_date} 데이터 결과 입니다.")
    st.write(
        """
        이 분석은 'self_similarity' 데이터에 대해 사분위수, IQR (사분위 범위), 이상치 탐지를 수행한 결과입니다. 
        이를 통해 데이터의 분포와 이상치를 시각화하고, 특정 이상치 기준에 따른 유저 행동을 분석합니다.
        """
    )
    st.write(
        """
        ##### 아래 통계 값들은 'self_similarity' 데이터의 분포와 이상치 탐지 결과를 나타냅니다. 
        - 일반적으로 **1.5x IQR 기준**을 적용하여 이상치를 탐지하지만 
        - 'self_similarity' 값이 0.97 이상이거나 1 미만인 데이터를 이상치로 처리하였습니다.
        """
    )
    return date_str


def self_show_metric(
    df, num_outliers_wide, filtered_outliers, mean_value, median_value, Q1, Q3, IQR
):
    # 통계 값 출력
    col0, col1 = st.columns(2)
    col0.metric("🔹 기존 이상치 개수 (1.5x IQR 기준)", num_outliers_wide)
    col1.metric(
        "🔹 특정 이상치 개수 (0.97 이상 또는 1 미만)", filtered_outliers.shape[0]
    )
    # 1행 4열로 정보 나누기
    col0, col1, col2, col3 = st.columns(4)

    # 첫 번째 줄
    col0.metric("🔹 평균(Mean)", f"{mean_value}")
    col1.metric("🔹 중앙값(Median)", f"{median_value}")
    col2.metric("🔹 1사분위수(Q1, 25%)", Q1)
    col3.metric("🔹 3사분위수(Q3, 75%)", Q3)

    # 두 번째 줄
    col0.metric("🔹 IQR(사분위 범위)", IQR)
    col1.metric(
        "🔹 이상치 기준 (1.5x IQR, 기존 넓은 기준) 하한", round((Q1 - 1.5 * IQR), 4)
    )
    col2.metric(
        "🔹 이상치 기준 (1.5x IQR, 기존 넓은 기준) 상한", round((Q3 + 1.5 * IQR), 4)
    )
    col3.metric("🔹 특정 이상치 기준", "0.97 ~ 1")
    outliers = df[df["self_similarity"] > Q3 + 1.5 * IQR]
    return outliers, filtered_outliers
