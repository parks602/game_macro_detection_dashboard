import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from datetime import timedelta, datetime
 
sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity_itemlog, setup_activity
from login.login_function import get_client_ip

def get_date_range():
    activity = setup_activity_itemlog()
    query= """SELECT min(logtime) mintime, max(logtime) maxtime
    FROM itemLog_Baphomet with (index(clx_logtime))"""
    df = activity.get_df(query)
    mindate = df['mintime'][0].strftime('%Y-%m-%d')
    maxdate = (df['maxtime'][0]+timedelta(days=1)).strftime('%Y-%m-%d')
    return(mindate, maxdate)
    

def background_generate(image_path, maker_func, df, key):
    st.session_state.graph_generating[key] = True
    try:
        maker_func(df, image_path)
    finally:
        st.session_state.graph_generating[key] = False


def get_image_data(date_str, end_date_str, selected_ip):
    activity = setup_activity_itemlog()
    query = """
    select srcAccountID, action, logtime 
    from itemLog_Baphomet with (index(clx_logtime))
    where 
    logtime >= '{date}' 
    and logtime < '{end_date}'
    and ip = '{ip}'
    """
    df = activity.get_df(query.format(date=date_str, end_date=end_date_str, ip=selected_ip))
    return df

def activity_graph_maker2(df, image_path, start_date_str, end_date_str, threshold):
    SRC_ACCOUNT_ID = "srcAccountID"
    LOGTIME = "logtime"
    DF_SESSION_COLUMNS = [
        "srcAccountID",
        "Session_Number",
        "Start_Time",
        "End_Time",
    ]
    plt.rcParams["font.family"] = "Malgun Gothic"

    df_grouped = df.groupby(SRC_ACCOUNT_ID, group_keys=False).apply(
        lambda group: assign_group(group, threshold))
    segments = (
        df_grouped.groupby(['srcAccountID', 'sub_group'])
        .agg(Start_Time=('logtime', 'first'), End_Time=('logtime', 'last'))
        .reset_index()
    )
    segments['End_Time'] = segments['End_Time'] + pd.Timedelta(seconds=1)
    sorted_ids = segments["srcAccountID"].sort_values().to_list()
    st.info("(2/3)데이터 정제 완료")
    fig = px.timeline(
        segments,
        x_start="Start_Time",
        x_end="End_Time",
        y="srcAccountID",
        title="User Active Times",
        labels={
            "srcAccountID": "srcAccountID",
            "Start_Time": "Login Start",
            "End_Time": "Login End",
        },
        category_orders={"srcAccountID": sorted_ids},
        color_discrete_sequence=["darkblue"],
    )

    min_time = pd.Timestamp(start_date_str)
    max_time = pd.Timestamp(end_date_str)

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="AID",
        yaxis_type="category",  # 범주형 y축
        showlegend=False,  # 범례 숨기기
        xaxis_range=[min_time, max_time],
        width=1200,  # 그래프의 가로 크기
        height=600,
        plot_bgcolor="lightyellow",  # 배경색
    )
    # y축을 시간 순서로 뒤집지 않으려면 아래 코드 생략 가능
    fig.update_yaxes(autorange="reversed")

    fig.write_image(image_path)
    
    
def assign_group(df_group, threshold):
    df_group = df_group.sort_values('logtime').reset_index(drop=True)
    df_group['timedelta'] = df_group['logtime'].diff().dt.total_seconds().fillna(0)
    df_group['sub_group'] = (df_group['timedelta']>threshold).cumsum()
    return df_group

def activity_graph_maker(df, image_path, threshold):

    SRC_ACCOUNT_ID = "srcAccountID"
    LOGTIME = "logtime"
    DF_SESSION_COLUMNS = [
        "srcAccountID",
        "Session_Number",
        "Start_Time",
        "End_Time",
    ]
    plt.rcParams["font.family"] = "Malgun Gothic"
    session_threshold = pd.Timedelta(seconds=threshold)
    records = []

    sorted_ids = df["srcAccountID"].value_counts().index.tolist()
    for user_id, group in df.groupby(SRC_ACCOUNT_ID):
        group = group.sort_values(LOGTIME).reset_index(drop=True)
        session_number = 0
        start_time = group.loc[0, LOGTIME]
        end_time = group.loc[0, LOGTIME] + pd.Timedelta(seconds=1)

        for i in range(1, len(group)):
            current_time = group.loc[i, LOGTIME]

            # 새로운 세션 감지
            if (current_time - end_time) > session_threshold:
                session_number += 1
                records.append([user_id, session_number, start_time, end_time])
                start_time = current_time
            elif i == len(group) - 1:
                # 마지막 세션 처리
                records.append(
                    [
                        user_id,
                        session_number,
                        start_time,
                        current_time + pd.Timedelta(seconds=1),
                    ]
                )
            end_time = current_time + pd.Timedelta(seconds=1)

    df_session = pd.DataFrame(records, columns=DF_SESSION_COLUMNS)
    st.info("(2/3)데이터 정제 완료")
    plt.rcParams["font.family"] = "Malgun Gothic"
    
    # 등장 순서에 맞춰 y축 정렬
    

    fig = px.timeline(
        df_session.sort_values(by="srcAccountID").reset_index(drop=True),
        x_start="Start_Time",
        x_end="End_Time",
        y="srcAccountID",
        title="User Active Times",
        labels={
            "srcAccountID": "srcAccountID",
            "Start_Time": "Login Start",
            "End_Time": "Login End",
        },
        category_orders={"srcAccountID": sorted_ids},
        color_discrete_sequence=["darkblue"],
    )

    min_time = pd.Timestamp(df_session["Start_Time"].dt.date.min()).replace(
        hour=0, minute=0, second=0
    )
    max_time = min_time + pd.Timedelta(days=1)

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="AID",
        yaxis_type="category",  # 범주형 y축
        showlegend=False,  # 범례 숨기기
        xaxis_range=[min_time, max_time],
        width=1200,  # 그래프의 가로 크기
        height=600,
        plot_bgcolor="lightyellow",  # 배경색
    )
    # y축을 시간 순서로 뒤집지 않으려면 아래 코드 생략 가능
    fig.update_yaxes(autorange="reversed")

    fig.write_image(image_path)

def image_path_return(date_str, end_date_str, selected_ip):
    selected_ip = str(selected_ip)
    second_image_path = os.path.join(
        os.getcwd(),  'graph', 'second', f"{selected_ip.replace('.', '_')}_{date_str.replace('-', '')}-{end_date_str.replace('-','')}.png"
    )
    seconds_image_path = os.path.join(
        os.getcwd(), 'graph', 'seconds', f"{selected_ip.replace('.', '_')}_{date_str.replace('-', '')}-{end_date_str.replace('-','')}.png"
    )
    minute_image_path = os.path.join(
        os.getcwd(), 'graph', 'minute', f"{selected_ip.replace('.', '_')}_{date_str.replace('-', '')}-{end_date_str.replace('-','')}.png"
    )
    return second_image_path, seconds_image_path, minute_image_path

def get_csv_download(date_str, end_date_str, selected_ip):
    df = get_image_data(date_str, end_date_str, selected_ip)
    aid_list = df['srcAccountID'].unique().tolist()
    return df.to_csv(index=False).encode('utf-8'), aid_list

def save_download_log(aid_list, reason):
    username = st.session_state["user_name"]
    logtime = datetime.now().replace(microsecond=0)
    ip = get_client_ip()
    
    activity = setup_activity()
    for aid in aid_list:
        query = """INSERT INTO download_logs (id, logtime, ip, subject_user_id, reason)
                    VALUES (?, ?, ?, ?, ?)"""
        values = [username, logtime, ip, aid, reason]
        activity.insert_login_with_execute(query, values)
        
