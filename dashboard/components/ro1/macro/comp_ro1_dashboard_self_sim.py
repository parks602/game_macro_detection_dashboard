import streamlit as st
import matplotlib.pyplot as plt


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
    return outliers


def self_show_graph(df, outliers):
    st.write("#### 자기 유사도 분포표")
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))

    # sns.boxplot(y=df["self_similarity"], ax=axes[0])
    axes[0].boxplot(df["self_similarity"])
    axes[0].set_title("Self-Similarity Distribution (Original)")
    axes[0].set_ylabel("Self-Similarity")
    axes[0].set_ylim(0.5, 1.1)  # Y축 범위 고정
    axes[0].grid(True, linestyle="--", alpha=0.7)

    # sns.histplot(
    #    df["self_similarity"], bins=30, kde=True, ax=axes[1], color="skyblue"
    # )
    axes[1].hist(
        df["self_similarity"],
        bins=30,
        color="skyblue",
        edgecolor="black",
        alpha=0.7,
    )
    axes[1].set_title("Self-Similarity Histogram")
    axes[1].set_ylabel("Frequency")

    # sns.histplot(
    #    outliers["self_similarity"], kde=True, ax=axes[2], color="red", bins=30
    # )
    axes[2].hist(
        outliers["self_similarity"],
        bins=30,
        color="red",
        edgecolor="black",
        alpha=0.7,
    )
    axes[2].set_title("Outliers Distribution")
    axes[2].set_ylabel("Frequency")

    st.pyplot(fig)


def self_show_bottom(filtered_outliers, Q1, Q3, IQR, num_outliers_wide):
    st.write(
        """
        - **박스 플롯**은 'self_similarity'의 전반적인 분포를 보여줍니다. 
        - **히스토그램**은 'self_similarity'의 빈도 분포를 나타내며, 정상 데이터와 이상치를 구분할 수 있습니다.
        - **이상치 분포**는 1.5x IQR을 초과하는 값들만 시각화하여, 이상치가 데이터에 미치는 영향을 보여줍니다.
        """
    )

    # 특정 이상치의 필터링 결과
    st.write("#### 특정 이상치의 분석 결과")
    st.write(
        """
        아래는 'self_similarity' 값이 0.97 이상이거나 1 미만인 데이터와 그 외 다른 이상치들을 보여줍니다. 
        이를 통해 특정 유저들이 매우 유사한 행동을 보였음을 알 수 있습니다. 이 데이터를 바탕으로 추가적인 분석이 필요할 수 있습니다.
        """
    )
    st.write(f"조건에 맞는 이상치 개수: {filtered_outliers.shape[0]}")

    # 데이터프레임을 가로로 꽉 차게 표시
    st.dataframe(filtered_outliers, use_container_width=True)

    st.write("---")
    # 설명 추가
    st.markdown(
        f"""
    ### 📊 IQR 기반 이상치 탐지 방법 설명
    IQR(Interquartile Range, 사분위 범위)을 사용하여 이상치를 탐지하는 방법은 데이터의 분포를 기반으로 이상치의 경계를 정의합니다. 이 방법의 적합성에 대한 주요 근거는 다음과 같습니다:

    1. **IQR(사분위 범위)**: 데이터의 중앙 50% 범위를 나타내며, Q1(25%)과 Q3(75%) 사이의 차이입니다. IQR은 데이터의 중심적인 경향을 나타내는 중요한 지표입니다.

    2. **이상치 탐지 공식**:
    - 하한 (Lower Bound) = Q1 - 1.5 * IQR
    - 상한 (Upper Bound) = Q3 + 1.5 * IQR
    - 이 범위를 벗어난 데이터는 이상치로 간주됩니다.

    3. **`1.5 * IQR`의 적합성**:
    - `1.5 * IQR` 기준은 통계학적으로 널리 사용되는 방법으로, 대부분의 데이터셋에서 효과적으로 이상치를 탐지합니다.
    - **강건성**: 이 기준은 극단적인 값에 민감하지 않으며, 데이터의 왜곡을 최소화합니다.
    - **통계적 검증**: `1.5 * IQR` 기준은 여러 실험을 통해 실용적이고 신뢰성 있는 방법으로 입증되었습니다.

    ### 🛑 매크로 유저 강력한 기준 (self_similarity > 0.97)
    

    - **이유**:매크로 유저를 더 강력하게 잡기 위해 `self_similarity` 값이 0.97 이상인 유저를 매크로 유저로 추정합니다. 이는 정상적인 유저의 유사도가 1에 가까워지지 않기 때문에, `self_similarity` 값이 0.97 이상인 경우 매크로 유저로 간주하는 매우 높은 기준을 설정한 것입니다.
    - **매크로 유저 의심**: 정상적인 유저는 `self_similarity` 값이 1에 가까워지는 경우가 거의 없지만, 매크로 유저는 반복적인 행동으로 인해 자기 자신과의 유사도가 매우 높을 수 있습니다.
    - **높은 기준**: `self_similarity > 0.97` 기준은 매크로 유저를 보다 강력하게 탐지하고 의심할 수 있는 기준입니다.

    ### 🔴 **매크로 의심 유저** 개수: **{filtered_outliers.shape[0]}명** 
    **매크로 유저로 의심되는 유저가 {filtered_outliers.shape[0]}명 발견되었습니다.** 이 유저들은 `self_similarity` 값이 0.97 이상이거나 1 미만인 유저들로, 의심이 가는 유저들입니다.

    ### 🔍 이상치 통계
    - **하한 (Lower Bound)**: {Q1 - 1.5 * IQR:.4f}
    - **상한 (Upper Bound)**: {Q3 + 1.5 * IQR:.4f}

    ### 🔹 기존 이상치 개수 (1.5x IQR 기준): {num_outliers_wide}개
    - **이상치 탐지 결과**를 바탕으로 1.5x IQR 기준 이상치 탐지 작업을 진행하였습니다. 이 값이 매우 유의미하며, 특정 유저들이 매우 유사한 행동을 보일 경우 이상치로 추출됩니다.
    """
    )
