import os
import sys
import pandas as pd
import plotly.express as px

sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity


def summary_load_data(date_str):
    activity = setup_activity()
    query = """
    SELECT * 
    FROM [dbo].[macro_user_summary] 
    WHERE Date <= '{date}' 
        and Date > DATEADD(DAY, -10, '{date}')"""

    df = activity.get_df(query.format(date=date_str))
    return df


def summary_calculate_metric(df, date_str):
    summary_counts = (
        df.groupby("distinction")["AID"]
        .nunique()
        .rename(
            {
                "detection": "매크로 탐지 유저",
                "suspicion": "매크로 의심 유저",
                "normal": "클린 유저",
                "block": "블럭된 유저",
            }
        )
    )
    # 오늘 날짜에 해당하는 신규 검출 유저 수 계산
    target_aids = df[(df["Date"] == date_str) & (df["distinction"] == "detection")][
        "AID"
    ]

    # 다른 날짜에서 "distinction" == "detection" 인 AID 목록
    other_aids = df[(df["Date"] != date_str) & (df["distinction"] == "detection")][
        "AID"
    ]

    # 다른 날짜에 없는 AID만 필터링
    unique_aids = target_aids[~target_aids.isin(other_aids)]

    # 고유한 AID 개수 출력
    new_detected_users = unique_aids.nunique()

    macro_count = summary_counts.get("매크로 탐지 유저", 0)
    suspicion_count = summary_counts.get("매크로 의심 유저", 0)
    block_aid = df[(df["Date"] == date_str) & (df["distinction"] == "block")][
        "AID"
    ].unique()
    block_count = df[
        (df["distinction"] == "detection") & (df["AID"].isin(block_aid))
    ].shape[0]
    normal_count = summary_counts.get("클린 유저", 0)
    return normal_count, macro_count, suspicion_count, block_count, new_detected_users


def summary_make_graph(
    df, normal_count, macro_count, suspicion_count, block_count, new_detected_users
):
    # 1. 전체 유저 분포 (정상, 매크로, 의심, 블럭)
    pie_data1 = pd.DataFrame(
        {
            "유저 유형": ["정상 유저", "매크로 유저", "의심 유저", "블럭 유저"],
            "수": [normal_count, macro_count, suspicion_count, block_count],
        }
    )
    fig1 = px.pie(pie_data1, names="유저 유형", values="수", title="🔍 전체 유저 비율")
    fig1.update_traces(textinfo="value+percent")

    # 2. 매크로 탐지 유저 vs 블럭된 유저
    pie_data2 = pd.DataFrame(
        {
            "유저 유형": ["매크로 탐지 유저", "블럭된 유저"],
            "수": [macro_count, block_count],
        }
    )
    fig2 = px.pie(
        pie_data2, names="유저 유형", values="수", title="🔍 매크로 탐지 vs 블럭된 유저"
    )
    fig2.update_traces(textinfo="value+percent")

    # 3. 매크로 탐지 유저 vs 신규 검출 유저
    pie_data3 = pd.DataFrame(
        {
            "유저 유형": ["매크로 탐지 유저", "신규 검출 유저"],
            "수": [macro_count, new_detected_users],
        }
    )
    fig3 = px.pie(
        pie_data3,
        names="유저 유형",
        values="수",
        title="🔍 매크로 탐지 vs 신규 검출 유저",
    )
    fig3.update_traces(textinfo="value+percent")

    # 4. 매크로 탐지 유저 vs 매크로 의심 유저
    pie_data4 = pd.DataFrame(
        {
            "유저 유형": ["매크로 탐지 유저", "매크로 의심 유저"],
            "수": [macro_count, suspicion_count],
        }
    )
    fig4 = px.pie(
        pie_data4,
        names="유저 유형",
        values="수",
        title="🔍 매크로 탐지 vs 매크로 의심 유저",
    )
    fig4.update_traces(textinfo="value+percent")

    # 5. 매크로 탐지 유저 중 reason 1 vs reason 2
    reason_1_count = len(df[df["reason"] == "action_one"]["AID"].unique())
    reason_2_count = len(df[df["reason"] == "action_diff"]["AID"].unique())
    reason_3_count = len(df[df["reason"] == "cosine_sim"]["AID"].unique())
    reason_4_count = len(df[df["reason"] == "self_sim"]["AID"].unique())

    pie_data5 = pd.DataFrame(
        {
            "유저 유형": [
                "멀티 클라이언트 동시 같은 액션",
                "멀티 클라이언트 동시 다른 액션",
                "유저간 행동 유사성 기반",
                "유저별 자기 유사도 기반",
            ],
            "수": [reason_1_count, reason_2_count, reason_3_count, reason_4_count],
        }
    )

    fig5 = px.pie(
        pie_data5,
        names="유저 유형",
        values="수",
        title="🔍 매크로 탐지 유저 분포",
    )
    fig5.update_traces(textinfo="value+percent")

    # 기존 계산된 값 사용
    reason_counts = {
        "멀티 클라이언트 동시 같은 액션": reason_1_count,
        "멀티 클라이언트 동시 다른 액션": reason_2_count,
        "유저 간 행동 유사성": reason_3_count,
        "유저별 자기 유사도": reason_4_count,
    }
    return fig1, fig2, fig3, fig4, fig5, reason_counts
