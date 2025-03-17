from same_time_diff_action_data import make_diff_action_data
from cosine_similarity_data import datamining, datamining_grapgh
from self_similarity_data import make_self_sim_data
from datetime import datetime, timedelta
from data_collector import collect_data
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
    grouped_users, df = datamining(yesterday, save_folder)
    datamining_grapgh(grouped_users, df, save_folder)
    make_self_sim_data(yesterday)
    make_diff_action_data(yesterday)
    collect_data(yesterday)
