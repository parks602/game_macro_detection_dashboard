import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity, setup_activity_datamining


def user_load_data(date_str):
    activity = setup_activity()
    query = """
    SELECT m1.*
    FROM [dbo].[macro_user_summary] m1
    INNER JOIN(
        SELECT AID, Date
        FROM [dbo].[macro_user_summary]
        WHERE distinction = 'detection' and Date <= '{date}' and Date > DATEADD(DAY, -10, '{date}')
        ) m2
    ON m1.AID = m2.AID AND m1.Date = m2.Date
    WHERE m1.Date <= '{date}' and m1.Date > DATEADD(DAY, -10, '{date}')
    """

    df = activity.get_df(query.format(date=date_str))
    return df


def user_make_pivot(df):
    detected_id = df["AID"].unique()
    pivot_df = df.pivot_table(
        index="AID", columns="reason", aggfunc="size", fill_value=0
    )
    pivot_df = (pivot_df > 0).astype(int).reset_index()
    pivot_df.columns = (
        "AID",
        "멀티 클라이언트 다른 행위",
        "자기 유사도",
        "멀티 클라이언트 같은 행위",
        "코사인 유사도",
    )
    return pivot_df, detected_id


def get_action_one_df(aid, macro_date, date_str):
    activity = setup_activity_datamining()
    query = f"""select * from Macro_multi_evidence_vol2 where AID = '{aid}' and Date = '{macro_date}'"""
    df = activity.get_df(query.format(date_str=date_str, aid=aid))
    activity.disconnect_from_db()
    return df


def get_action_diff(macro_date, date_str):
    activity = setup_activity()
    query = f"""select srcAccountID as AID , ip, logtime, Action from macro_user_same_time_diff_action_detail where Date = '{macro_date}'"""
    df = activity.get_df(query.format(date_str=date_str))
    activity.disconnect_from_db()
    return df


def get_self_diff(aid, macro_date, date_str):
    activity = setup_activity()
    query = f"""select srcAccountID as AID, cosine_similarity, self_similarity, logtime_count from macro_user_self_similarity
                where Date = '{macro_date}' and srcAccountID = '{aid}'"""
    df = activity.get_df(query.format(date_str=date_str, aid=aid))
    activity.disconnect_from_db()
    return df


def get_cosine(macro_date, date_str):
    activity = setup_activity()
    query = f"""select srcAccountID as AID, Group_name, Total_logtime_Count, Duplication_count, Ratio, IPs
                from macro_user_cosine_similarity_detail where Date = '{macro_date}'"""
    df = activity.get_df(query.format(date_str=date_str))
    activity.disconnect_from_db()
    return df
