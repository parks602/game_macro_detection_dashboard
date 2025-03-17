import pandas as pd
import numpy as np
import warnings
from datetime import datetime, timedelta
from db_functions import setup_activity, update_environment_file
from queries import GET_DAILY_USER_ACTIVITY_ALL_ACTION

warnings.simplefilter("ignore", UserWarning)


def make_diff_action_data(yesterday):
    activity = setup_activity(db_type="itemlog")
    df = activity.get_df(GET_DAILY_USER_ACTIVITY_ALL_ACTION.format(date=yesterday))
    activity.disconnect_from_db()
    print(df.head(5))
    print(df.shape)
    df = df[["IP", "logtime", "action", "srcAccountID"]]
    print(df.shape)
    grouped = df.groupby(["IP", "logtime"]).filter(lambda x: len(x) > 1)
    print(grouped.shape)
    # 'IP'와 'logtime'이 같고 'action'과 'srcAccountID'가 다른 행 선택
    result = grouped.groupby(["IP", "logtime"]).filter(
        lambda x: x["action"].nunique() > 1 and x["srcAccountID"].nunique() > 1
    )
    result = result.groupby("srcAccountID").filter(lambda x: len(x) > 10)
    result = result.drop_duplicates()
    print(result.head(5))
    print(result.shape)
    result["Date"] = yesterday
    activity = setup_activity("pdu")
    activity.insert_dataframe_replace_date(
        "macro_user_same_time_diff_action_detail", result
    )
    activity.disconnect_from_db()
    return result


if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    result = make_diff_action_data(yesterday)
    #
