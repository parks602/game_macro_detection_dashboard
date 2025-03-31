import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity


def cs_load_data(date_str):
    activity = setup_activity()
    query = """
    SELECT * 
    FROM [dbo].[macro_user_summary] 
    WHERE Date <= '{date}' 
        and Date > DATEADD(DAY, -10, '{date}')"""

    df = activity.get_df(query.format(date=date_str))
    return df


def cs_calculate_user_counts(df, date_str):
    target_aids = df[(df["Date"] == date_str) & (df["distinction"] == "detection")][
        "AID"
    ]
    other_aids = df[(df["Date"] != date_str) & (df["distinction"] == "detection")][
        "AID"
    ]
    unique_aids = target_aids[~target_aids.isin(other_aids)]
    new_detected_users = unique_aids.nunique()

    all_user_count = df["AID"].nunique()
    macro_user = df[df["distinction"] == "detection"]["AID"].nunique()
    suspic_user = df[df["distinction"] == "suspicion"]["AID"].nunique()
    block_aids = df[(df["Date"] == date_str) & (df["distinction"] == "block")][
        "AID"
    ].unique()
    block_user = df[
        (df["distinction"] == "detection") & (df["AID"].isin(block_aids))
    ].shape[0]
    clean_user = all_user_count - macro_user - suspic_user - block_user
    return (
        new_detected_users,
        all_user_count,
        macro_user,
        suspic_user,
        block_user,
        clean_user,
    )
