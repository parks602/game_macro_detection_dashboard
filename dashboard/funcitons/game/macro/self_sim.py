import os
import sys
import matplotlib.pyplot as plt

sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity


def self_load_data(date_str):
    activity = setup_activity()
    query = """
    SELECT * 
    FROM [dbo].[macro_user_self_similarity] 
    WHERE Date = '{date}'"""

    df = activity.get_df(query.format(date=date_str))
    return df


def self_calculate_values(df):
    Q1 = round(df["self_similarity"].quantile(0.25), 4)  # 1사분위수 (25%)
    Q3 = round(df["self_similarity"].quantile(0.75), 4)  # 3사분위수 (75%)
    IQR = round(Q3 - Q1, 4)  # 사분위 범위 (Interquartile Range)

    # 기존 1.5 * IQR 이상치 개수
    outliers_wide = df[
        (
            (df["self_similarity"] < (Q1 - 1.5 * IQR))
            | (df["self_similarity"] > (Q3 + 1.5 * IQR))
        )
        & (df["self_similarity"] < 1)
    ]
    num_outliers_wide = outliers_wide.shape[0]

    # 특정 이상치 기준: self_similarity > 0.97, self_similarity < 1
    double_narrow_outliers = df[
        (df["self_similarity"] > 0.97) & (df["self_similarity"] < 1)
    ]
    # 추가 조건: logtime_count > 100, self_similarity != 1
    filtered_outliers = double_narrow_outliers[
        (double_narrow_outliers["logtime_count"] > 100)
        & (double_narrow_outliers["self_similarity"] != 1)
    ]
    # 평균, 중앙값 계산
    mean_value = round(df["self_similarity"].mean(), 4)
    median_value = round(df["self_similarity"].median(), 4)
    return (
        df,
        num_outliers_wide,
        filtered_outliers,
        mean_value,
        median_value,
        Q1,
        Q3,
        IQR,
        num_outliers_wide,
    )


