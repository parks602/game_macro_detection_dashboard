import os
import sys
import matplotlib.pyplot as plt

sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity_datamining


def stsa_load_data(date_str):
    activity = setup_activity_datamining()
    query = """SELECT * 
        FROM [dbo].[macro_user_same_time_diff_action_detail] 
        WHERE Date = '{date}'"""

    df = activity.get_df(query.format(date=date_str))
    return df


def stda_gropuby_df(df):
    ip_logtime_unique = (
        df.groupby("ip")
        .agg(
            unique_logtime_count=("logtime", "nunique"),
            unique_AID_count=("srcAccountID", "nunique"),
        )
        .reset_index()
        .sort_values("unique_logtime_count", ascending=True)
        .reset_index(drop=True)
    )
    return ip_logtime_unique


# 📌 4. IP별 logtime 분석 시각화
def stda_plot_ip_logtime_distribution(ip_logtime_unique):
    ip_logtime_unique["cumulative"] = ip_logtime_unique["unique_logtime_count"].cumsum()
    ip_logtime_unique["cumulative"] /= ip_logtime_unique["cumulative"].iloc[-1]

    fig, ax1 = plt.subplots(figsize=(14, 10))

    bars = ax1.bar(
        ip_logtime_unique["ip"],
        ip_logtime_unique["unique_logtime_count"],
        color="blue",
        alpha=0.7,
        label="IP별 발생 수",
    )

    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:,}",
            ha="center",
            va="bottom",
            fontsize=10,
            color="blue",
        )

    ax1.set_xlabel("IP", fontsize=12)
    ax1.set_ylabel("IP별 발생 수", fontsize=12, color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.set_xticklabels(ip_logtime_unique["ip"], rotation=90)

    ax2 = ax1.twinx()
    ax2.plot(
        ip_logtime_unique["ip"],
        ip_logtime_unique["unique_AID_count"],
        color="green",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=5,
        label="유저 수",
    )
    ax2.set_ylabel("IP별 유저 수", fontsize=12, color="green")
    ax2.tick_params(axis="y", labelcolor="green")

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(
        ip_logtime_unique["ip"],
        ip_logtime_unique["cumulative"],
        color="red",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=5,
        label="누적 분포",
    )
    ax3.set_ylabel("누적 분포", fontsize=12, color="red")
    ax3.tick_params(axis="y", labelcolor="red")

    return fig


def select_top_user(df):
    top_users = (
        df.groupby("srcAccountID")
        .agg(
            count=("srcAccountID", "size"),
            ip_list=("ip", lambda x: list(x.unique())),
        )
        .reset_index()
        .sort_values("count", ascending=False)
        .head(20)
    )
    return top_users


def stda_top20_user_graph(top_users):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        top_users["srcAccountID"].astype(str),
        top_users["count"],
        color="skyblue",
        edgecolor="black",
    )

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:,}",
            ha="center",
            va="bottom",
            fontsize=10,
            color="blue",
        )

    plt.xlabel("유저 (srcAccountID)", fontsize=12)
    plt.ylabel("중복 행동 횟수", fontsize=12)
    plt.xticks(rotation=45)

    return plt
