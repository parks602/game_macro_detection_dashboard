import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import time
import sys, os
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db_functions import setup_activity
from src.queries import GET_UI_DATA_SELF_SIM_USER


def dashboard_self_sim():
    st.title("유저별 행동 유사성 기반 세부 내용")

    with st.sidebar:
        if st.button("시간연장"):
            st.session_state["last_active"] = time.time()
            st.success("세션 연장 완료")

    # Session State에서 날짜 저장 및 불러오기
    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = datetime.now().date() - timedelta(days=1)
    if "dataframes" not in st.session_state:
        st.session_state["dataframes"] = {}
    if "selected_group_id" not in st.session_state:
        st.session_state["selected_group_id"] = None
    if "group_list" not in st.session_state:
        st.session_state["group_list"] = None
    # 날짜 입력 위젯
    date_selected = st.date_input(
        "날짜를 선택하세요", value=st.session_state["selected_date"]
    )
    current_time = datetime.now().time()
    yesterday_date = datetime.today().date() - timedelta(days=1)
    analysis_date = datetime.now().date() - timedelta(days=2)

    # 날짜 유효성 검사
    if date_selected != st.session_state["selected_date"]:
        st.session_state["selected_date"] = date_selected
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
        save_folder = (
            "C:/Users/pdu_admin/Desktop/projects/RO1_Dashboard_with_streamlit/result/graph/%s/%s/%s"
            % (
                date_str[:4],
                date_str[5:7],
                date_str[8:10],
            )
        )
        image_base_path = save_folder

        activity = setup_activity(db_type="pdu")
        try:
            st.session_state["dataframes"]["save_df"] = activity.get_df(
                GET_UI_DATA_SELF_SIM_USER.format(date=st.session_state["selected_date"])
            )
        except Exception as e:
            st.error("데이터 로딩 중 오류가 발생했습니다.")
            st.error(e)
            return
        finally:
            activity.disconnect_from_db()

        df = st.session_state["dataframes"]["save_df"]
        # 사분위수 및 IQR 계산
        Q1 = round(df["self_similarity"].quantile(0.25), 4)  # 1사분위수 (25%)
        Q3 = round(df["self_similarity"].quantile(0.75), 4)  # 3사분위수 (75%)
        IQR = round(Q3 - Q1, 4)  # 사분위 범위 (Interquartile Range)

        # 기존 1.5 * IQR 이상치 개수
        outliers_wide = df[
            (
                (df["self_similarity"] < (Q1 - 1.5 * IQR))
                | (df["self_similarity"] > (Q3 + 1.5 * IQR))
            )
            & (df["self_similarity"] < 1)
        ]
        num_outliers_wide = outliers_wide.shape[0]

        # 특정 이상치 기준: self_similarity > 0.97, self_similarity < 1
        double_narrow_outliers = df[
            (df["self_similarity"] > 0.97) & (df["self_similarity"] < 1)
        ]
        # 추가 조건: logtime_count > 100, self_similarity != 1
        filtered_outliers = double_narrow_outliers[
            (double_narrow_outliers["logtime_count"] > 100)
            & (double_narrow_outliers["self_similarity"] != 1)
        ]
        num_double_narrow_outliers = filtered_outliers.shape[0]
        # 평균, 중앙값 계산
        mean_value = round(df["self_similarity"].mean(), 4)
        median_value = round(df["self_similarity"].median(), 4)

        # Streamlit 출력
        st.title("📊 Self-Similarity Analysis and Outlier Detection")
        st.info(f"{st.session_state['selected_date']} 데이터 결과 입니다.")

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

        # 해당 범위의 이상치 및 정상 데이터
        outliers = df[df["self_similarity"] > Q3 + 1.5 * IQR]
        normal_data = df[df["self_similarity"] <= Q3 + 1.5 * IQR]

        # 그래프들 출력
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

        # 그래프 간격 조정
        plt.tight_layout()
        st.write("#### 자기 유사도 분포표")

        st.pyplot(fig)

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
