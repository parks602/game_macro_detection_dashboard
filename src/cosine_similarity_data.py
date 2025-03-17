from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
import plotly.express as px
import requests
from db_functions import setup_activity
from queries import GET_DAILY_USER_ACTIVITY


# 코사인 유사도를 통한 유저간 유사도 도출 및 DB 저장 함수수
def datamining(yesterday, save_folder):
    # 데이터베이스 연결
    activity = setup_activity(db_type="itemlog")
    # 어제 날짜의 유저 활동 데이터 불러오기 쿼리(GET_DAILY_USER_ACTIVITY)는 queries.py에 정의
    df_row = activity.get_df(GET_DAILY_USER_ACTIVITY.format(date=yesterday))
    # 데이터프레임 생성
    save_df = pd.DataFrame(
        columns=[
            "Date",
            "All_user",
            "All_group",
            "Multi_user_group",
            "Multi_user_group_all_user",
        ]
    )
    # 필요한 컬럼만 추출(쿼리 문이 범용적으로 사용되기 때문에)
    df = df_row[["srcAccountID", "logtime"]]
    # logtime 컬럼을 datetime 형식으로 변환
    df["logtime"] = pd.to_datetime(df["logtime"])

    standard_time = yesterday + " 00:00:00"
    # 접속 세션 구분 기준 (2분 이상)
    session_threshold = pd.Timedelta(minutes=2)

    # 접속 기록 테이블 생성
    # 유저별로 접속 기록을 저장하기위해 위에서 정한 세션 기준으로 logtime을 그룹화
    # srcAccountID, Session_Number, Start_Time, End_Time 컬럼을 가진 데이터프레임 생성
    records = []
    print("data load complete")
    for user_id, group in df.groupby("srcAccountID"):
        group = group.sort_values("logtime").reset_index(drop=True)
        session_number = 0
        start_time = group.loc[0, "logtime"]
        end_time = group.loc[0, "logtime"]
        for i in range(1, len(group)):
            current_time = group.loc[i, "logtime"]

            # 새로운 세션 감지
            if (current_time - end_time) > session_threshold:
                session_number += 1
                records.append([user_id, session_number, start_time, end_time])
                start_time = current_time

            # 접속 종료 시간 갱신
            end_time = current_time
    df_session = pd.DataFrame(
        records, columns=["srcAccountID", "Session_Number", "Start_Time", "End_Time"]
    )
    print("data grouping complete")

    # 하루 24시간을 초 단위로 타임라인 생성
    seconds_in_day = 24 * 60 * 60

    # 접속 상태 타임라인 초기화
    user_timelines = {
        user: np.zeros(seconds_in_day, dtype=int)
        for user in df_session["srcAccountID"].unique()
    }

    # 각 ID의 접속 구간에 대해 타임라인 값 설정
    for _, row in df_session.iterrows():
        user_id = row["srcAccountID"]
        start_idx = int(
            (row["Start_Time"] - pd.Timestamp(standard_time)).total_seconds()
        )
        end_idx = int((row["End_Time"] - pd.Timestamp(standard_time)).total_seconds())

        # 접속 구간에 대해 1 설정
        user_timelines[user_id][start_idx : end_idx + 1] = 1

    print("data timeline complete")
    # 코사인 유사도 계산
    timelines_array = np.array(list(user_timelines.values()))
    user_ids = list(user_timelines.keys())
    similarity_matrix = cosine_similarity(timelines_array)
    print("similarity matrix complete")
    similarities = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]

    # 유사도 분포 히스토그램 그리기
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    plt.hist(similarities, bins=50, color="blue", edgecolor="black")
    plt.title("Cosine Similarity Distribution")
    plt.xlabel("Cosine Similarity")
    plt.ylabel("Frequency")
    plt.savefig(
        "%s/all_user_histogram.png" % (save_folder),
        dpi=300,
        bbox_inches="tight",
    )

    # 임계값 0.99 이상인 유저 연결
    threshold = 0.99
    G = nx.Graph()

    # 노드 추가
    G.add_nodes_from(user_ids)

    # 유사도 임계값 이상인 노드 연결
    for i in range(len(user_ids)):
        for j in range(i + 1, len(user_ids)):
            if similarity_matrix[i][j] >= threshold:
                G.add_edge(user_ids[i], user_ids[j])

    # 연결된 구성 요소(그룹) 찾기
    groups = list(nx.connected_components(G))
    print("grouping complete")
    # 그룹별 유저 목록 생성(딕셔너리 구조조)
    grouped_users = {f"Group {i+1}": list(group) for i, group in enumerate(groups)}

    group_durations = {}

    for group_name, user_list in grouped_users.items():
        total_duration = 0
        total_sessions = 0

        for user_id in user_list:
            user_timeline = user_timelines[user_id]
            session_duration = np.sum(user_timeline)  # 접속 초 개수 합산
            total_duration += session_duration
            total_sessions += 1

        # 평균 접속 시간 계산 (초 단위 → 분으로 변환)
        avg_duration_minutes = (
            (total_duration / total_sessions) / 60 if total_sessions > 0 else 0
        )
        group_durations[group_name] = avg_duration_minutes
    result = {key: len(value) for key, value in grouped_users.items()}
    one_item = {key: value for key, value in grouped_users.items() if len(value) == 1}

    # 유사도 99.9% 이상인 그룹 유저 슬라이싱싱
    two_or_more_items = {
        key: value for key, value in grouped_users.items() if len(value) >= 2
    }
    # 데이터 베이스 입력을 위한 데이터 생성
    data = {
        "Date": [yesterday],  # 날짜
        "All_user": [len(user_ids)],  # 전체 유저 수
        "All_group": [len(result)],  # 전체 그룹 수
        "Multi_user_group": [len(two_or_more_items)],  # 다중 유저 그룹 수
        "Multi_user_group_all_user": [
            sum(len(value) for value in grouped_users.values() if len(value) >= 2)
        ],  # 다중 유저 그룹의 총 유저 수
    }
    # 기존 save_df가 존재하면 추가, 존재하지 않으면 새로 생성
    try:
        save_df = pd.concat([save_df, pd.DataFrame(data)], ignore_index=True)
    except NameError:
        save_df = pd.DataFrame(data)
    print("Insert macro_user_groups Start")
    activity.disconnect_from_db()
    activity = setup_activity(db_type="pdu")
    activity.insert_dataframe_replace_date("macro_user_groups", save_df)

    # 유사도 분포 히스토그램 데이터 생성
    bins = np.linspace(0, 1, 11)
    counts, bin_edges = np.histogram(similarities, bins=bins)

    # DataFrame 생성
    range_histogram = pd.DataFrame(
        {
            "Date": yesterday,
            "Range_Start": bin_edges[:-1],
            "Range_End": bin_edges[1:],
            "Count": counts,
        }
    )

    print("Insert range_histogram Start")
    activity.insert_dataframe_replace_date("range_histogram", range_histogram)
    analysis_keys = [key for key, value in grouped_users.items() if len(value) > 1]

    # DB 저장을 위한 데이터 프레임 생성
    save_df_row = pd.DataFrame(
        columns=[
            "Date",
            "srcAccountID",
            "Group_name",
            "Total_logtime_Count",
            "Duplication_count",
            "Ratio",
            "IPs",
        ]
    )
    # 그룹별 유저 IP 정보, API 사용 불가로 사용하지 않음.
    save_ip_info = pd.DataFrame(
        columns=["Date", "ip", "city", "region", "country", "loc", "org", "postal"]
    )
    for key_name in analysis_keys:
        analysis_users = grouped_users[key_name]
        filtered_df = df_row[df_row["srcAccountID"].isin(analysis_users)]

        # 다른 srcAccountID와 logtime, ip가 같으나 SID나 MapName이 다른 경우
        logtime_counts = (
            filtered_df.groupby("srcAccountID")["logtime"]
            .count()
            .reset_index(name="Total_logtime_Count")
        )

        merged_df = pd.merge(
            filtered_df, filtered_df, on=["logtime"], suffixes=("_x", "_y")
        )
        # with ThreadPoolExecutor() as executor:
        #     results = list(executor.map(get_ip_info, filtered_df["ip"].unique()))
        # 유효한 결과만 필터링
        # valid_results = [result for result in results if result]
        # 결과를 DataFrame으로 변환
        # ip_df = pd.DataFrame(valid_results)[
        #     ["ip", "city", "region", "country", "loc", "org", "postal"]
        # ]
        # ip_df.insert(0, "Date", yesterday)

        # 조건: 서로 다른 srcAccountID + SID 또는 MapName이 다름
        filtered_df2 = merged_df[
            (merged_df["srcAccountID_x"] != merged_df["srcAccountID_y"])
        ]

        # srcAccountID별로 갯수 세기
        mismatch_counts = (
            filtered_df2.groupby("srcAccountID_x")["logtime"]
            .nunique()
            .reset_index(name="Duplication_count")
        )

        # 결과 병합
        result = pd.merge(
            logtime_counts,
            mismatch_counts,
            how="left",
            left_on="srcAccountID",
            right_on="srcAccountID_x",
        )
        result = result.drop(columns=["srcAccountID_x"]).fillna(0)
        result["Duplication_count"] = result["Duplication_count"].astype(int)
        result["Ratio"] = result["Duplication_count"] / result["Total_logtime_Count"]

        # IPs 컬럼 추가
        result["IPs"] = result["srcAccountID"].apply(
            lambda x: get_unique_ips(x, filtered_df2)
        )
        result.insert(0, "Date", yesterday)
        result.insert(2, "Group_name", key_name)

        save_df_row = pd.concat([save_df_row, result], ignore_index=True)
        # save_ip_info = pd.concat([save_ip_info, ip_df], ignore_index=True)
    save_df_row["IPs"] = save_df_row["IPs"].apply(str)
    activity.insert_dataframe_replace_date("macro_user_groups_detail", save_df_row)

    return grouped_users, df_session


def get_unique_ips(src_account_id, filtered_df2):
    # srcAccountID를 기준으로 ip_x, ip_y에서 고유 IP 목록 생성
    ips_x = set(
        filtered_df2[filtered_df2["srcAccountID_x"] == src_account_id]["IP_x"].unique()
    )
    ips_y = set(
        filtered_df2[filtered_df2["srcAccountID_y"] == src_account_id]["IP_y"].unique()
    )
    # 두 목록을 합쳐서 고유 IP 목록 생성
    return list(ips_x.union(ips_y))


# 보안상 API 사용 금지지
def get_ip_info(ip):
    url = f"https://ipinfo.io/{ip}/json?token=14ec64f7013dc4"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# 그룹별 유저 접속 시간 그래프 생성
def datamining_grapgh(grouped_users, df, save_folder):
    plt.rcParams["font.family"] = "Malgun Gothic"
    two_or_more_items = {
        key: value for key, value in grouped_users.items() if len(value) >= 2
    }
    sample_data = sorted(two_or_more_items.items(), key=lambda x: len(x[1]))

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # top_5_groups에 대해 그래프 생성
    for group_name, user_list in sample_data:
        # 해당 그룹의 접속 기록 데이터를 모은 리스트
        group_data = []

        # 각 유저별 접속 시간 데이터를 group_data 리스트에 추가
        for user_id in user_list:
            user_data = df[df["srcAccountID"] == user_id]

            for _, row in user_data.iterrows():
                start_time = row["Start_Time"]
                end_time = row["End_Time"]
                group_data.append(
                    {"AID": user_id, "start_time": start_time, "end_time": end_time}
                )

        # group_data를 DataFrame으로 변환
        group_df = pd.DataFrame(group_data)

        # plotly.express로 간트 차트 생성
        fig = px.timeline(
            group_df.sort_values(by="AID").reset_index(drop=True),
            x_start="start_time",
            x_end="end_time",
            y="AID",
            title=f"{group_name} User Active Times",
            labels={"AID": "AID", "start_time": "Login Start", "end_time": "Login End"},
        )
        min_time = pd.Timestamp(group_df["start_time"].dt.date.min()).replace(
            hour=0, minute=0, second=0
        )
        max_time = min_time + pd.Timedelta(days=1)
        # 레이아웃 설정
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="AID",
            yaxis_type="category",  # 범주형 y축
            showlegend=False,  # 범례 숨기기
            xaxis_range=[min_time, max_time],
            width=1200,  # 그래프의 가로 크기
            height=600,
        )
        # 그래프 저장
        image_path = os.path.join(
            save_folder, f"{group_name}_access_gantt_chart_plotly.png"
        )
        fig.write_image(image_path)
    print(f"그래프 이미지가 '{save_folder}' 폴더에 저장되었습니다.")


def main():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    save_folder = (
        "C:/Users/pdu_admin/Desktop/projects/RO1_Dashboard_with_streamlit/result/graph/%s/%s/%s"
        % (
            yesterday[:4],
            yesterday[5:7],
            yesterday[8:10],
        )
    )
    # update_environment_file()
    grouped_users, df = datamining(yesterday, save_folder)
    datamining_grapgh(grouped_users, df, save_folder)


if __name__ == "__main__":
    main()
