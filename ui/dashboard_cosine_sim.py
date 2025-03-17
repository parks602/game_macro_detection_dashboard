import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import time
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db_functions import setup_activity
from src.queries import (
    GET_UI_DATA_GROUP_USER,
    GET_UI_DATA_GROUP_USER_DETAIL,
    GET_UI_DATA_RAGNE_HISTOGRAM,
)


def dashboard_cos_sim():
    st.title("유저간 행동 유사성 기반 세부 내용")

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
    yesterday_date = datetime.today().date()-timedelta(days=1)
    analysis_date = datetime.now().date() - timedelta(days=2)
    if date_selected != st.session_state["selected_date"]:
        st.session_state["selected_date"] = date_selected
        st.session_state["last_active"] = time.time()
        if date_selected < datetime.strptime("2025-03-09", "%Y-%m-%d").date():
            st.error(
                f"2025년 3월 9일 부터 선택 가능합니다. {analysis_date} 날짜 데이터가 출력됩니다."
            )
            time.sleep(3)
            st.session_state["selected_date"] = analysis_date
        elif (date_selected == yesterday_date and current_time.hour < 15) or (date_selected > yesterday_date):
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

        st.session_state["dataframes"]["save_df"] = activity.get_df(
            GET_UI_DATA_GROUP_USER.format(date=st.session_state["selected_date"])
        )
        st.session_state["dataframes"]["range_histogram"] = activity.get_df(
            GET_UI_DATA_RAGNE_HISTOGRAM.format(date=st.session_state["selected_date"])
        )
        st.session_state["dataframes"]["save_df_row"] = activity.get_df(
            GET_UI_DATA_GROUP_USER_DETAIL.format(date=st.session_state["selected_date"])
        )
        st.title("📊 Cosine-Similarity Analysis and Clustering")
        st.info(f"{st.session_state['selected_date']} 데이터 결과 입니다.")

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
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔹 전체 분석 유저", st.session_state["dataframes"]["save_df"]['All_user'])
        col2.metric('🔹 전체 그룹 수', st.session_state["dataframes"]["save_df"]['All_group'])
        col3.metric('🔹 매크로 의심 그룹 수', st.session_state["dataframes"]["save_df"]['Multi_user_group'])
        col4.metric('🔹 매크로 의심 유저 수', st.session_state["dataframes"]["save_df"]['Multi_user_group_all_user'])
        st.write("---")
        col1, col2 = st.columns([5, 5])
        filtered_df = st.session_state["dataframes"]["save_df"]
        filtered_df = filtered_df[filtered_df["Date"] == date_str]


        # 유저별 유사도 분포 히스토그램 출력
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
                st.session_state["dataframes"]["range_histogram"],
                use_container_width=True,
            )

        st.write("-----")

        # Multi_user_group_all_user 리스트
        st.write("### Multi_user_group_all_user 리스트")
        st.write("Multi_user_group의 목록과 각 그룹에 속한 유저 ID 및 유저 수를 보여줍니다.")
        group_list_data = st.session_state["dataframes"]["save_df_row"]
        group_list_data = group_list_data[group_list_data["Date"] == date_str]
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
        grouped.rename(
            columns={"srcAccountID": "unique_srcAccountID_count"}, inplace=True
        )
        grouped["srcAccountID_list"] = grouped["srcAccountID_list"].apply(str)

        st.dataframe(
            grouped.set_index(grouped.columns[0]),
            use_container_width=True,
        )

        if not grouped.empty:  # 데이터가 있을 때만 처리
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

        # 해당 그룹 사용자의 활동 상세 내용
        grouped_data = group_list_data[
            group_list_data["Group_name"] == selected_group_id
        ]
        st.write("해당 그룹 사용자의 24시간 활동 데이터")
        st.image(
            "%s/Group %s_access_gantt_chart_plotly.png"
            % (image_base_path, st.session_state["selected_group_id"][6:]),
            use_container_width=True,
        )

        st.subheader("코사인 유사도를 활용한 이유")
        with st.expander("코사인 유사도란?"):
            st.write("""
            코사인 유사도는 두 개의 벡터(유저의 행동 패턴)가 얼마나 유사한지를 측정하는 지표입니다.
            - **값이 1에 가까울수록 행동 패턴이 거의 동일**
            - **0에 가까울수록 행동 패턴이 다름**
            - **음수 값** 이라면 정반대의 행동 패턴
            """)
        st.subheader("선택한 threshold 0.99를 유지하려면?")
        col1, col2 = st.columns(2)
        col1.metric("하루 총 행동 횟수", "1,440 (분 단위)")
        col2.metric("허용되는 차이", "1~2분 이하")
        st.write("""
        만약 하루 동안 1440개의 행동이 기록된다면,
        - 유사도 **99.9% 이상을 유지하려면 1~2분 이하만 다르게 행동** 해야 합니다.
        - **10분 이상 차이가 나면 유사도는 급격히 감소**합니다.
        """
        )
        st.write("""
        우리는 이 탐지 기법에서는 유저들의 액션을 체크한 것이 아닌 **접속 여부**를 따졌습니다.
        - 1분간 액션 로그가 하나라도 있다면 그 시간에 접속 중인 것으로 판단합니다.
        - 이후 모든 유저들의 1분단위 행동 여부를 가지고 코사인 유사도를 체크합니다.""")
"""
        # 해당 그룹 사용자의 IP 분석
        st.write("해당 그룹 사용자의 IP 분석")
        st.dataframe(
            grouped_data.sort_values(by="Total_logtime_Count", ascending=False),
            use_container_width=True,
        )


import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import time
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db_functions import setup_activity
from src.queries import (
    GET_UI_DATA_GROUP_USER,
    GET_UI_DATA_GROUP_USER_DETAIL,
    GET_UI_DATA_RAGNE_HISTOGRAM,
)


def dashboard():
    st.title("유저간 행동 유사성 기반 세부 내용")

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
    if date_selected != st.session_state["selected_date"]:
        st.session_state["selected_date"] = date_selected
        st.session_state["last_active"] = time.time()
        if date_selected < datetime.strptime("2025-02-25", "%Y-%m-%d").date():
            st.error(
                "2025년 2월 25일 부터 선택 가능합니다. 어제 날짜 데이터가 출력됩니다."
            )
            st.session_state["selected_date"] = datetime.now().date() - timedelta(
                days=1
            )
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

        st.session_state["dataframes"]["save_df"] = activity.get_df(
            GET_UI_DATA_GROUP_USER.format(date=st.session_state["selected_date"])
        )
        st.session_state["dataframes"]["range_histogram"] = activity.get_df(
            GET_UI_DATA_RAGNE_HISTOGRAM.format(date=st.session_state["selected_date"])
        )
        st.session_state["dataframes"]["save_df_row"] = activity.get_df(
            GET_UI_DATA_GROUP_USER_DETAIL.format(date=st.session_state["selected_date"])
        )

        col1, col2 = st.columns([5, 5])

        filtered_df = st.session_state["dataframes"]["save_df"]
        filtered_df = filtered_df[filtered_df["Date"] == date_str]
        st.dataframe(filtered_df)
        st.write("All_user = Action=1 500회 이상 활동한 사용자 수")
        st.write("All_group = 코사인 유사도 분석을 통해 생성된 그룹 수")
        st.write("Multi_user_group = All_group 중 2명 이상의 사용자가 속한 그룹 수")
        st.write(
            "Multi_user_group_all_user = All_user 중 2명 이상의 사용자가 속한 그룹 수"
        )

        with col1:
            st.write("유저별 유사도 분포 히스토그램")
            st.image(
                "%s/all_user_histogram.png" % (image_base_path),
                use_container_width=True,
            )

        with col2:
            st.write("유저별 유사도 분포 히스토그램 데이터")
            st.dataframe(
                st.session_state["dataframes"]["range_histogram"],
                use_container_width=True,
            )

        st.write("-----")
        st.write("Multi_user_group_all_user 리스트")
        group_list_data = st.session_state["dataframes"]["save_df_row"]
        group_list_data = group_list_data[group_list_data["Date"] == date_str]
        grouped = (
            group_list_data.groupby("Group_name")
            .agg(
                unique_srcAccountID_count=("srcAccountID", "nunique"),
                srcAccountID_list=("srcAccountID", lambda x: list(x.unique())),
            )
            .sort_values(by="unique_srcAccountID_count", ascending=False)
            .reset_index(drop=False)
        )
        grouped.rename(
            columns={"srcAccountID": "unique_srcAccountID_count"}, inplace=True
        )
        grouped["srcAccountID_list"] = grouped["srcAccountID_list"].apply(str)

        st.dataframe(
            grouped.set_index(grouped.columns[0]),
            use_container_width=True,
        )

        if not grouped.empty:  # 데이터가 있을 때만 처리
            group_list = (
                grouped.sort_values(by="unique_srcAccountID_count", ascending=False)[
                    "Group_name"
                ]
                .unique()
                .tolist()
            )
            st.session_state["group_list"] = group_list

        selected_group_id = st.selectbox(
            "Select a group", st.session_state["group_list"]
        )
        st.session_state["selected_group_id"] = selected_group_id

        st.write("Selected group:", selected_group_id)
        st.write("해당 그룹 사용자의 활동")
        grouped_data = group_list_data[
            group_list_data["Group_name"] == selected_group_id
        ]
        st.write("해당 그룹 사용자의 24시간 활동 데이터")
        st.image(
            "%s/Group %s_access_gantt_chart_plotly.png"
            % (image_base_path, st.session_state["selected_group_id"][6:]),
            use_container_width=True,
        )

        st.write("해당 그룹 사용자의 IP 분석")
        st.dataframe(
            grouped_data.sort_values(by="Total_logtime_Count", ascending=False),
            use_container_width=True,
        )
"""
"""
            with col4:
                st.write("해당 그룹 사용자의 IP 분석")
                ip_info_data = st.session_state["dataframes"]["save_ip_info"]
                ip_info_data = ip_info_data[ip_info_data["Date"] == date_str]
                st.dataframe(
                    grouped_data.sort_values(by="Total_logtime_Count", ascending=False),
                    use_container_width=True,
                )
                grouped_data = grouped_data.copy()
                grouped_data["IPs"] = grouped_data["IPs"].apply(
                    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                )
                all_ips = sum(grouped_data["IPs"], [])  # 모든 IP 리스트를 합침
                unique_ips = list(set(all_ips))
                ip_info_data = ip_info_data[ip_info_data["ip"].isin(unique_ips)]
                ip_info_data = ip_info_data.drop_duplicates()
                st.dataframe(
                    ip_info_data,
                    use_container_width=True,
                )
            with col5:
                st.write("해당 그룹 사용자의 IP 위치 분포")

                ip_info_data[["latitude", "longitude"]] = ip_info_data["loc"].str.split(
                    ",", expand=True
                )
                ip_info_data["latitude"] = ip_info_data["latitude"].astype(float)
                ip_info_data["longitude"] = ip_info_data["longitude"].astype(float)
                st.map(ip_info_data[["latitude", "longitude"]])
                """
