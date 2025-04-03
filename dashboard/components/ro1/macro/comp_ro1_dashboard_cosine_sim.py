import streamlit as st
from pathlib import Path

# 📌 최상위 프로젝트 폴더 설정
BASE_DIR = Path('.')


def cosine_show_top_sentence():
    date_selected = st.session_state["selected_date"]
    date_str = date_selected.strftime("%Y-%m-%d")
    save_folder = (
        BASE_DIR
        / ".."
        / "datamining"
        / "ro1"
        / "macro"
        / "result"
        / "graph"
        / date_str[:4]
        / date_str[5:7]
        / date_str[8:10]
    ).resolve().as_posix()
    print_date = date_selected.strftime("%Y년 %m월 %d일")
    st.info(f"{print_date} 데이터 결과 입니다.")
    st.write(
        """
        이 분석은 유저간 'Cosine_similarity'를 도출, 유사도 99% 이상의 유저들을 하나의 그룹으로 클러스터링 실시합니다.
        생성되는 그룹 중 2명 이상의 유저를 포함하는 그룹을 매크로 유저 의심 그룹으로 설정합니다.
        """
    )
    st.write("#### 지표 설명")
    st.write(
        """
        - **All_user**: Action=1을 500회 이상 수행한 유저 수
        - **All_group**: 코사인 유사도 분석을 통해 생성된 전체 그룹 수
        - **Multi_user_group**: 2명 이상의 유저들이 속한 그룹 수
        - **Multi_user_group_all_user**: Multi_user_group의 전체 유저 수 
        """
    )
    return date_str, save_folder


def cosine_show_metric(df):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔹 전체 분석 유저", df["All_user"])
    col2.metric("🔹 전체 그룹 수", df["All_group"])
    col3.metric("🔹 매크로 의심 그룹 수", df["Multi_user_group"])
    col4.metric("🔹 매크로 의심 유저 수", df["Multi_user_group_all_user"])
    st.write("---")


def cosine_show_histogram(histo_df, image_base_path):
    # 유저별 유사도 분포 히스토그램 출력
    col1, col2 = st.columns([5, 5])
    with col1:
        st.write("### 유사도 분포 히스토그램")
        st.image(
            "%s/all_user_histogram.png" % (image_base_path),
            use_container_width=True,
        )

    # 유저별 유사도 분포 데이터 출력
    with col2:
        st.write("### 유사도 분포 히스토그램 데이터")
        st.dataframe(
            histo_df,
            use_container_width=True,
        )

    st.write("-----")


def cosine_show_user_list(row_df, date_str):
    # Multi_user_group_all_user 리스트
    st.write("### Multi_user_group_all_user 리스트")
    st.write(
        "Multi_user_group의 목록과 각 그룹에 속한 유저 ID 및 유저 수를 보여줍니다."
    )
    group_list_data = row_df[row_df["Date"] == date_str]
    grouped = (
        group_list_data.groupby("Group_name")
        .agg(
            unique_srcAccountID_count=("srcAccountID", "nunique"),
            srcAccountID_list=(
                "srcAccountID",
                lambda x: list(x.unique()),
            ),  # 유저별 목록
        )
        .sort_values(by="unique_srcAccountID_count", ascending=False)
        .reset_index(drop=False)
    )
    grouped.rename(columns={"srcAccountID": "unique_srcAccountID_count"}, inplace=True)
    grouped["srcAccountID_list"] = grouped["srcAccountID_list"].apply(str)

    st.dataframe(
        grouped.set_index(grouped.columns[0]),
        use_container_width=True,
    )
    return grouped


def cosine_show_group_graph(grouped, image_base_path):
    if "group_list" not in st.session_state:
        st.session_state["group_list"] = None
    group_list = (
        grouped.sort_values(by="unique_srcAccountID_count", ascending=False)[
            "Group_name"
        ]
        .unique()
        .tolist()
    )
    st.session_state["group_list"] = group_list
    selected_group_id = st.selectbox(
        "그룹을 선택하세요", st.session_state["group_list"]
    )
    st.session_state["selected_group_id"] = selected_group_id

    st.write("### 선택한 그룹의 활동 내용")
    st.write(f"선택한 그룹: {selected_group_id}")
    st.write("해당 그룹 사용자의 24시간 활동 데이터")
    st.image(
        "%s/Group %s_access_gantt_chart_plotly.png"
        % (image_base_path, st.session_state["selected_group_id"][6:]),
        use_container_width=True,
    )


def cosine_show_bottom():
    st.subheader("코사인 유사도를 활용한 이유")
    with st.expander("코사인 유사도란?"):
        st.write(
            """
        코사인 유사도는 두 개의 벡터(유저의 행동 패턴)가 얼마나 유사한지를 측정하는 지표입니다.
        - **값이 1에 가까울수록 행동 패턴이 거의 동일**
        - **0에 가까울수록 행동 패턴이 다름**
        - **음수 값** 이라면 정반대의 행동 패턴
        """
        )
    st.subheader("선택한 threshold 0.99를 유지하려면?")
    col1, col2 = st.columns(2)
    col1.metric("하루 총 행동 횟수", "1,440 (분 단위)")
    col2.metric("허용되는 차이", "1~2분 이하")
    st.write(
        """
    만약 하루 동안 1440개의 행동이 기록된다면,
    - 유사도 **99.9% 이상을 유지하려면 1~2분 이하만 다르게 행동** 해야 합니다.
    - **10분 이상 차이가 나면 유사도는 급격히 감소**합니다.
    """
    )
    st.write(
        """
    우리는 이 탐지 기법에서는 유저들의 액션을 체크한 것이 아닌 **접속 여부**를 따졌습니다.
    - 1분간 액션 로그가 하나라도 있다면 그 시간에 접속 중인 것으로 판단합니다.
    - 이후 모든 유저들의 1분단위 행동 여부를 가지고 코사인 유사도를 체크합니다."""
    )
