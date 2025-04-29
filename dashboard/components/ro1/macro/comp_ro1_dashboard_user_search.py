import streamlit as st
from datetime import timedelta
from pathlib import Path

from funcitons.ro1.macro.user_search import (
    get_action_one_df,
    get_action_diff,
    get_self_diff,
    get_cosine,
)

BASE_DIR = Path(".")
def user_show_top_sentence():
    date_selected = st.session_state["selected_date"]
    date_str = date_selected.strftime("%Y-%m-%d")
    print_date = date_selected.strftime("%Y년 %m월 %d일")
    print_pre_date = (date_selected - timedelta(days=9)).strftime("%Y년 %m월 %d일")
    st.markdown(
        f"#### {print_pre_date} 부터 {print_date}까지 10일간의 데이터 통계입니다."
    )
    return date_str


def user_show_pviot_df(pivot_df):
    st.write("##### 매크로 탐지 유저의 근거 표, 1:탐지, 0:미탐지")
    st.dataframe(pivot_df, use_container_width=True)


def user_selector(detected_id):
    selected_aid = st.selectbox("근거를 찾아볼 AID를 고르세요", detected_id)
    return selected_aid


def user_show_middle(df, selected_aid):
    all_macro_detected_date = df[
        (df["AID"] == selected_aid) & (df["distinction"] == "detection")
    ]["Date"].sort_values()
    st.session_state["macro_date"] = (
        df[(df["AID"] == selected_aid) & (df["distinction"] == "detection")]["Date"]
        .max()
        .strftime("%Y-%m-%d")
    )
    st.subheader(f"선택하신 {st.session_state['user_aid']} 매크로 탐지 내역입니다.")
    date_list = all_macro_detected_date.astype(str).tolist()
    formateed_text = ", ".join(date_list)
    st.markdown(
        f"##### {selected_aid} 는 10일간 총 {len(all_macro_detected_date)}회, {formateed_text} 에 매크로로 검출 되었습니다."
    )
    col1, col2 = st.columns([7, 3])
    with col1:
        user_date_selected = st.selectbox(
            "유저 세부 사항 요청 날짜를 선택하세요", all_macro_detected_date
        )
        if user_date_selected:
            st.session_state["macro_date"] = str(user_date_selected)

    st.write(
        f"##### {selected_aid} 는 {st.session_state['macro_date']} 검출 증거 입니다."
    )
    # 선택한 AID가 바뀌면 세션 업데이트 후 재실행
    if selected_aid != st.session_state["user_aid"]:
        st.session_state["user_aid"] = selected_aid
        st.rerun()

    reason_dict = {
        "action_diff": "멀티 클라이언트 다른 행위",
        "self_sim": "자기 유사도",
        "action_one": "멀티 클라이언트 같은 행위",
        "cosine_sim": "코사인 유사도",
    }

    df["Date"] = df["Date"].astype(str)
    user_logs = df[
        (df["AID"] == selected_aid)
        & (df["distinction"] == "suspicion")
        & (df["Date"] == str(st.session_state["macro_date"]))
    ]
    st.write("#### 📌 분석 요약")
    reasons = user_logs["reason"].unique()
    with col2:
        st.write("데이터 다운로드")
        if st.button(
            label=f"{selected_aid}, {st.session_state['macro_date']} 데이터 다운로드"
        ):
            with st.spinner("데이터 생성중입니다. 잠시 기다려주세요."):
                st.error("아직 데이터 다운로드 기능은 제공되지 않습니다.")
                # excel_file = data_download(selected_aid, st.session_state['macro_date'], reasons, reason_dict)
                # st.info("데이터가 생성되었습니다. 아래 다운로드 버튼을 눌러주세요")
                # st.download_button(label = "다운로드 실행",
                #                    data = excel_file)
                #                    file_name = f"{selected_aid}_{st.session_state['macro_date']}_row_data.xlsx"
                #                    mime = "application/vnd.openxlmformats-officedocumet.spreadsheetml.sheet")
    reason_text = " ,   ".join([reason_dict.get(r, r) for r in reasons])
    st.info(f"탐지 사유 {len(reasons)}개 :  {reason_text}")
    return reasons, reason_dict


def user_show_reason(reasons, reason_dict):
    # 각 사유별 상세 검출 내역 출력
    for reason in reasons:
        st.markdown("---")
        st.write(f"##### 📌 {reason_dict[reason]}")
        if reason == "action_diff":
            show_action_diff(
                st.session_state["macro_date"],
                st.session_state["selected_date"],
                st.session_state["user_aid"],
            )
        elif reason == "self_sim":
            show_self_sim(
                st.session_state["selected_date"],
                st.session_state["user_aid"],
                st.session_state["macro_date"],
            )
        elif reason == "action_one":
            show_action_one(
                st.session_state["selected_date"],
                st.session_state["user_aid"],
                st.session_state["macro_date"],
            )
        elif reason == "cosine_sim":
            show_cosine_sim(
                st.session_state["selected_date"],
                str(st.session_state["user_aid"]),
                st.session_state["macro_date"],
            )


def show_action_one(date_str, aid, macro_date):
    # DB 연결 (datamining DB 사용)
    df = get_action_one_df(aid, macro_date, date_str)
    active_ip = df["IP"].unique()
    ip_list_str = ", ".join(active_ip)
    st.markdown("##### 멀티 클라이언트 동시 사냥 검출 내역")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("활동 IP", ip_list_str)
    col2.metric("전체 유효 활동", df["Total_action_count"][0])
    col3.metric("동시 사냥 활동", df["Overlap_count"][0])
    col4.metric("동시 사냥 비율", f"{df['Overlap_percentage'][0]}%")
    st.info(
        f"같은 IP에서 다른 계정과 동시 사냥 비율이 {df['Overlap_percentage'][0]}%로 나타나 매크로 유저로 탐지외었습니다."
    )
    st.write("###### 해당 근거 출처 데이터, 테이블 : Macro_multi_evidence_vol2")
    st.dataframe(df.drop_duplicates(), use_container_width=True)


def show_action_diff(macro_date, date_str, aid):
    df = get_action_diff(macro_date, date_str)
    user_df = df[df["AID"] == aid]
    active_ip = user_df["ip"].unique()
    ip_list_str = ", ".join(active_ip)

    unique_logtime_count = user_df["logtime"].nunique()

    st.markdown("##### 멀티 클라이언트 다른 액션 검출 내역")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("해당 유저가 활동한 IP 리스트", ip_list_str)
    with col2:
        st.metric(
            "해당 유저가 다른 유저와 동시에 다른 액션을 한 기록 수",
            f"{unique_logtime_count}건",
        )
    st.info(
        f"같은 IP에서 다른 계정과 동시에 다른 액션을 {unique_logtime_count}회 하여 매크로 유저로 탐지외었습니다."
    )
    st.write(
        "###### 해당 근거 출처 데이터, 테이블 : macro_user_same_time_diff_action_detail"
    )
    st.dataframe(user_df.reset_index(drop=True), use_container_width=True)


def show_self_sim(date_str, aid, macro_date):
    df = get_self_diff(aid, macro_date, date_str)
    logtime_count = df["logtime_count"].iloc[0]
    self_sim = round(df["self_similarity"].iloc[0], 4)
    cosine_sim = round(df["cosine_similarity"].iloc[0], 4)

    st.markdown("##### 자기 유사도 기반 검출 내역")
    st.markdown(
        f"""
    - 검사 유효 logtime이 **{logtime_count}**으로 100분 이상 활동했습니다.  
    - 자기유사도는 **{self_sim}**입니다.  
    - 행동 벡터 간 코사인 유사도 평균은 **{cosine_sim}**입니다.
    """
    )
    st.info(
        f"자기유사도는 **{self_sim}**로 기준치 0.97을 초과했기에 매크로 유저로 탐지되었습니다."
    )
    st.write("###### 해당 근거 출처 데이터, 테이블 : macro_user_self_similarity")
    st.dataframe(df, use_container_width=True)


def show_cosine_sim(date_str, aid, macro_date):
    print(macro_date)
    # 이미지 파일 경로 설정
    
    save_folder = (
        BASE_DIR
        / ".."
        / "datamining"
        / "ro1"
        / "macro"
        / "result"
        / "graph"
        / macro_date[:4]
        / macro_date[5:7]
        / macro_date[8:10]
    ).resolve().as_posix()
    df = get_cosine(macro_date, date_str)

    user_df = df[df["AID"] == aid].reset_index(drop=True)
    group_name = user_df["Group_name"][0]
    logtime_count = df[df["AID"] == aid]["Total_logtime_Count"].values[0]
    group_df = df[df["Group_name"] == group_name].reset_index(drop=True)
    group_user_count = group_df["AID"].nunique()

    cosine_similarity = round(df[df["AID"] == aid]["Ratio"].values[0], 4)

    st.markdown("##### 유저간 코사인 유사도 기반 검출 내역")
    st.markdown(
        f"""
    - 검사 유효 logtime 횟수는 **{logtime_count}**입니다.  
    - 해당 유저의 소속 그룹 번호는 **{group_name}**입니다.  
    - 해당 그룹에 속한 유저 수는 **{group_user_count}**입니다.
    """
    )
    st.info(
        f"코사인 유사도가 기준치 0.99을 초과하는 유저가 **{group_user_count}**명으로 1명 이상이기에 매크로 유저로 탐지되었습니다."
    )
    st.write("###### 해당 근거 출처 데이터, 테이블 : macro_user_groups_detail")
    st.dataframe(group_df, use_container_width=True)
    st.write("###### 해당 그룹 사용자의 24시간 활동 데이터")
    st.image(
        "%s/Group %s_access_gantt_chart_plotly.png" % (save_folder, group_name[6:]),
        use_container_width=True,
    )
