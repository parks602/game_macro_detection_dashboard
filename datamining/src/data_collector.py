import pandas as pd
from datetime import datetime, timedelta
from db_functions import setup_activity
from queries import GET_MULTI_CHAR_USER, GET_MULTI_CHAR_USER_DIFF_ACTION_USER, GET_COSINE_SIMILARITY_USER, GET_SELF_SIMILARITY_USER, GET_ALL_ACTIVE_USER, GET_BLOKED_USER
import warnings

warnings.simplefilter("ignore", UserWarning)

def collect_data(yesterday):
    # 어제 날짜
    # DF_SA동시행동(ACTION1)
    activity = setup_activity("datamining")
    df_sa = activity.get_df(GET_MULTI_CHAR_USER.format(date=yesterday))
    df_sa['reason'] = 'action_one'
    activity.disconnect_from_db()
    # 전체 활동 유저
    activity = setup_activity("datamining_row")
    all_active_user_df = activity.get_df(GET_ALL_ACTIVE_USER.format(date=yesterday))
    activity.disconnect_from_db()
    # 동시행동(DIFF)
    activity = setup_activity("pdu")
    df_da = activity.get_df(GET_MULTI_CHAR_USER_DIFF_ACTION_USER.format(date=yesterday))
    df_da['reason'] = 'action_diff'
    # 코사인유사도
    df_cosine = activity.get_df(GET_COSINE_SIMILARITY_USER.format(date=yesterday))
    df_cosine['reason'] = 'cosine_sim'
    # 자기유사도
    df_selfco = activity.get_df(GET_SELF_SIMILARITY_USER.format(date=yesterday))
    df_selfco['reason'] = 'self_sim'
    # 블럭유저
    df_blocked = activity.get_df(GET_BLOKED_USER.format(date=yesterday))
    df_blocked['AID'] = df_blocked['AID'].astype(int)
    df_blocked['reason'] = None
    df_blocked['Date']=yesterday
    df_blocked['distinction'] = 'block'
    df_all = pd.concat([df_sa, df_da, df_cosine, df_selfco])
    df_all['AID']= df_all['AID'].astype(str)
    df_all_adis = df_all['AID'].unique()
    df_all = df_all.reset_index(drop=True)
    df_all['distinction'] = 'suspicion'
    df_all['Date'] = yesterday
    aid_counts = df_all['AID'].value_counts()
    valid_aids = aid_counts[aid_counts > 2].index
    df_valid = df_all[df_all['AID'].isin(valid_aids)]
    df_blocked = df_blocked[df_blocked['AID'].isin(valid_aids)]
    df_detect = df_valid[['AID']].drop_duplicates().copy()
    df_detect['distinction'] = 'detection'
    df_detect['Date'] = yesterday
    df_detect['reason'] = None
    all_active_user_df = all_active_user_df[~all_active_user_df['AID'].isin(df_all_adis)]
    all_active_user_df['Date'] = yesterday
    all_active_user_df['reason'] = None
    all_active_user_df['distinction'] = 'normal'
    insert_df = pd.concat([all_active_user_df, df_detect, df_all, df_blocked])
    insert_df['AID'] = insert_df['AID'].astype(str)
    activity.insert_dataframe_replace_date('macro_user_summary', insert_df)

if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterdays = ['2025-04-13','2025-04-14','2025-04-12','2025-04-11','2025-04-10']
    for yesterday in yesterdays:
        collect_data(yesterday)
