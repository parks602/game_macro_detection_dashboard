from same_time_diff_action_data import make_diff_action_data
from cosine_similarity_data import datamining, datamining_grapgh
from self_similarity_data import make_self_sim_data
from datetime import datetime, timedelta
from data_collector import collect_data
import time

if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    save_folder = (
        "C:/Users/pdu_admin/Desktop/projects/RO1_Dashboard_with_streamlit/result/graph/%s/%s/%s"
        % (
            yesterday[:4],
            yesterday[5:7],
            yesterday[8:10],
        )
    )
    start_time = time.time()
    grouped_users, df = datamining(yesterday, save_folder)
    end_time = time.time()
    print(f"코사인 유사도 실행시간 : {end_time - start_time} 초")

    datamining_grapgh(grouped_users, df, save_folder)
    start_time = time.time()
    make_self_sim_data(yesterday)
    end_time = time.time()
    print(f"자기 유사도 실행시간 : {end_time - start_time} 초")
    start_time = time.time()
    make_diff_action_data(yesterday)
    end_time = time.time()
    print(f"다른 액션 동일 IP 실행시간 : {end_time - start_time} 초")
    collect_data(yesterday)
