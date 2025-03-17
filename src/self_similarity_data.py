import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings

# import seaborn as sns
# import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from db_functions import setup_activity, update_environment_file
from queries import GET_DAILY_USER_ACTIVITY_ALL_ACTION

warnings.simplefilter("ignore", UserWarning)


def make_self_sim_data(yesterday):
    activity = setup_activity(db_type="itemlog")
    df = activity.get_df(GET_DAILY_USER_ACTIVITY_ALL_ACTION.format(date=yesterday))
    activity.disconnect_from_db()
    # 1) 중복 제거: 'Action', 'logtime', 'srcAccountID' 기준
    df = df[["action", "logtime", "srcAccountID"]]
    df = df.drop_duplicates(subset=["action", "logtime", "srcAccountID"])

    # 2) 'logtime'을 datetime 형식으로 변환 후 인덱스로 설정
    df["logtime"] = pd.to_datetime(df["logtime"])
    df.set_index("logtime", inplace=True)

    # 3) 각 srcAccountID별로 logtime 단위 갯수를 계산
    logtime_counts = df.groupby("srcAccountID").resample("min").action.count()

    # 4) logtime_count가 10 이상인 srcAccountID만 필터링
    valid_users = logtime_counts.groupby("srcAccountID").count()
    valid_users = valid_users[valid_users >= 10].index

    # 유효한 유저들만 데이터프레임에서 필터링
    df_filtered = df[df["srcAccountID"].isin(valid_users)]

    # 5) srcAccountID별로 그룹화하고 각 유저에 대해 액션 벡터를 계산
    def calculate_self_similarity(user_df):
        # 1분 단위로 리샘플링하고 각 액션별 빈도 수 계산
        action_counts = (
            user_df.resample("min").action.value_counts().unstack(fill_value=0)
        )

        # 6) 액션 벡터가 모두 0인 행을 삭제
        action_counts = action_counts.loc[(action_counts != 0).any(axis=1)]

        # 7) 현재 벡터와 이전 벡터 간의 코사인 유사도를 계산
        cosine_similarities = []

        for i in range(1, len(action_counts)):
            vec1 = action_counts.iloc[i - 1].values.reshape(1, -1)
            vec2 = action_counts.iloc[i].values.reshape(1, -1)
            similarity = cosine_similarity(vec1, vec2)[0, 0]  # 코사인 유사도 계산
            cosine_similarities.append(similarity)

        # 8) 코사인 유사도의 평균 계산
        avg_cosine_similarity = (
            np.mean(cosine_similarities) if cosine_similarities else 0
        )

        # 9) 유저의 코사인 유사도 표준편차 (σ) 계산
        sigma = np.std(cosine_similarities) if cosine_similarities else 0

        if avg_cosine_similarity == 0:
            H = 0.5  # 코사인 유사도가 0일 때는 변화를 극대화하여 H를 0으로 설정
        else:
            H = 1 - 0.5 * sigma

        # 11) 측정된 logtime 단위 갯수 계산
        logtime_count = len(action_counts)

        # 결과 반환 (소수점 4자리로 반올림)
        return pd.Series(
            {
                "cosine_similarity": round(
                    avg_cosine_similarity, 4
                ),  # 이전 벡터와 현재 벡터 간 평균 코사인 유사도
                "self_similarity": round(
                    H, 4
                ),  # 계산된 자기 유사도 (소수점 4자리로 반올림)
                "logtime_count": logtime_count,  # 측정된 logtime 단위 갯수
            }
        )

    # 12) srcAccountID별로 그룹화하여 위의 함수 적용
    result = df_filtered.groupby("srcAccountID").apply(calculate_self_similarity)
    result = result.reset_index()
    print(result.head())

    result = result[result["logtime_count"] >= 10]
    print(result.shape)

    result["Date"] = yesterday
    activity = setup_activity("pdu")
    activity.insert_dataframe_replace_date("macro_user_self_similarity", result)
    activity.disconnect_from_db()
    return result


if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    result = make_self_sim_data(yesterday)
    #
    # draw_graph(result)
