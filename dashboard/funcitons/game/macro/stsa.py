import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity_datamining


def stsa_load_data(date_str):
    activity = setup_activity_datamining()
    query = """SELECT *
                FROM [DataMining].[dbo].[Macro_multi_evidence_vol2]
                WHERE Date = '{date}'
                """
    df = activity.get_df(query.format(date=date_str))
    return df


def stsa_filter_macro_users(df):
    """매크로 의심 유저 필터링"""
    return df[
        (df["Total_action_count"] >= 1000) & (df["Overlap_percentage"] > 50)
    ].reset_index(drop=True)


def stsa_compute_statistics(macro_df, df):
    """대시보드 통계 정보 계산"""
    return {
        "macro_users": macro_df["AID"].nunique(),
        "unique_ips": macro_df["IP"].nunique(),
        "total_users": df["AID"].nunique(),
        "avg_actions": round(macro_df["Total_action_count"].mean()),
        "avg_overlap": round(macro_df["Overlap_count"].mean()),
    }


def stsa_process_ip_data(df):
    """IP별 통계 데이터 생성"""
    aid_count = (
        df.groupby("IP")["AID"]
        .nunique()
        .reset_index()
        .rename(columns={"AID": "AID_count"})
    )
    agg_df = (
        df.groupby("IP")[["Overlap_count", "Total_action_count"]].mean().reset_index()
    )

    result_df = df.merge(aid_count, on="IP").merge(
        agg_df, on="IP", suffixes=("", "_mean")
    )
    result_df[["Overlap_count_mean", "Total_action_count_mean"]] = result_df[
        ["Overlap_count_mean", "Total_action_count_mean"]
    ].round(1)

    return (
        result_df[["IP", "AID_count", "Overlap_count_mean", "Total_action_count_mean"]]
        .drop_duplicates()
        .sort_values("AID_count", ascending=False)
        .reset_index(drop=True)
    )
