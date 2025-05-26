import streamlit as st

from ...comp_common import date_selector, ip_selector, start_date_selector,   end_date_selector

from .comp_ro1_dashboard_cs import (
    cs_display_metrics,
    cs_display_pie_charts,
    cs_show_block_warning,
    cs_show_top_sentence,
)
from funcitons.ro1.macro.cs import (
    cs_load_data,
    cs_calculate_user_counts,
)


def dashboard_CS():
    st.title("RO1 바포메트 서버 유저 현황")
    date_selector()

    date_str = cs_show_top_sentence()
    df = cs_load_data(date_str)
    (
        new_detected_users,
        all_user_count,
        macro_user,
        suspic_user,
        block_user,
        clean_user,
    ) = cs_calculate_user_counts(df, date_str)
    # 제재 비율 계산
    block_ratio = round(block_user / macro_user, 2)
    block_percentage = round(block_ratio * 100, 2)
    cs_show_block_warning(block_ratio, block_percentage)

    # 메트릭 표시
    cs_display_metrics(
        all_user_count,
        clean_user,
        block_user,
        suspic_user,
        macro_user,
        new_detected_users,
    )

    # 그래프 표시
    cs_display_pie_charts(macro_user, suspic_user, block_user, clean_user)


from .comp_ro1_dashboard_summary import (
    summary_show_second_metric,
    summary_show_bottom,
    summary_show_expanders,
    summary_show_explain,
    summary_show_first_metric,
    summary_show_top_sentence,
)
from funcitons.ro1.macro.summary import (
    summary_make_graph,
    summary_calculate_metric,
    summary_load_data,
)


def dashboard_summary():
    st.title("매크로 탐지 대시보드 소개")
    summary_show_expanders()
    date_selector()
    st.markdown("### 🔥 탐지 현황 요약")
    date_str = summary_show_top_sentence()
    df = summary_load_data(date_str)
    normal_count, macro_count, suspicion_count, block_count, new_detected_users = (
        summary_calculate_metric(df, date_str)
    )
    summary_show_first_metric(normal_count, macro_count, suspicion_count, block_count)
    summary_show_second_metric(df)

    st.subheader("10일간 탐지된 유저 현황")
    fig1, fig2, fig3, fig4, fig5, reason_counts = summary_make_graph(
        df, normal_count, macro_count, suspicion_count, block_count, new_detected_users
    )
    col99, blank0, col98 = st.columns([3, 1, 6])
    with col99:
        st.plotly_chart(fig1)
    with col98:
        summary_show_explain(normal_count, macro_count, suspicion_count, block_count)

    st.write("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.subheader("📊 매크로 탐지 vs 블럭된 유저")
        st.plotly_chart(fig2)
    with col2:
        st.subheader("📊 매크로 탐지 vs 신규 검출 유저")
        st.plotly_chart(fig3)
    with col3:
        st.subheader("📊 매크로 탐지 vs 매크로 의심 유저")
        st.plotly_chart(fig4)
    st.write("---")
    col4, blank0, col5 = st.columns([4, 1, 5])
    with col4:
        st.subheader("매크로 의심 유저 유형 분포")

        st.plotly_chart(fig5)
    with col5:
        summary_show_bottom(reason_counts)


from .comp_ro1_dashboard_user_search import (
    user_show_top_sentence,
    user_show_pviot_df,
    user_selector,
    user_show_middle,
    user_show_reason,
)
from funcitons.ro1.macro.user_search import user_load_data, user_make_pivot


def dashboard_user_detail():
    st.title("유저별 매크로 탐지 근거")
    date_selector()

    date_str = user_show_top_sentence()
    df = user_load_data(date_str)
    pivot_df, detected_id = user_make_pivot(df)
    user_show_pviot_df(pivot_df)
    selected_aid = user_selector(detected_id)
    reasons, reason_dict = user_show_middle(df, selected_aid)
    user_show_reason(reasons, reason_dict)


from funcitons.ro1.macro.stsa import (
    stsa_load_data,
    stsa_filter_macro_users,
    stsa_compute_statistics,
    stsa_process_ip_data,
)

from .comp_ro1_dashboard_stsa import (
    stsa_show_top_sentence,
    stsa_show_metrics,
    stsa_show_dataframes,
)


def dashboard_same_time_same_action():
    st.title("멀티 클라이언트 동시 같은 행동")
    date_selector()

    date_str = stsa_show_top_sentence()
    df = stsa_load_data(date_str)
    macro_df = stsa_filter_macro_users(df)
    stats = stsa_compute_statistics(macro_df, df)
    result_df = stsa_process_ip_data(df)

    stsa_show_metrics(stats)
    stsa_show_dataframes(result_df, df)


from funcitons.ro1.macro.stda import (
    stda_load_data,
    stda_gropuby_df,
    stda_plot_ip_logtime_distribution,
    stda_top20_user_graph,
    select_top_user,
)

from .comp_ro1_dashboard_stda import (
    stda_show_top_sentence,
    stda_show_metrics,
    stda_show_graph_logtime,
    stda_show_df_logtime,
    stda_show_graph_summary,
    stda_show_graph_top_users,
    stda_show_dataframe_top_user,
)


def dashboard_same_time_diff_action():
    st.title("멀티 클라이언트 동시 다른 행동")
    date_selector()
    date_str = stda_show_top_sentence()
    df = stda_load_data(date_str)
    ip_logtime_unique = stda_gropuby_df(df)
    stda_show_metrics(df)

    fig = stda_plot_ip_logtime_distribution(ip_logtime_unique)

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        stda_show_graph_logtime(fig)
    with col2:
        stda_show_df_logtime(ip_logtime_unique)
    stda_show_graph_summary()

    st.write("---")

    top_users = select_top_user(df)
    stda_show_graph_top_users(stda_top20_user_graph(top_users))


from .comp_ro1_dashboard_cosine_sim import (
    cosine_show_top_sentence,
    cosine_show_metric,
    cosine_show_histogram,
    cosine_show_user_list,
    cosine_show_group_graph,
    cosine_show_bottom,
)
from funcitons.ro1.macro.cosine_sim import cosine_load_data


def dashboard_cos_sim():
    st.title("유저간 행동 유사성 기반 세부 내용")
    date_selector()
    date_str, save_folder = cosine_show_top_sentence()

    df, histo_df, row_df = cosine_load_data(date_str)

    cosine_show_metric(df)
    cosine_show_histogram(histo_df, save_folder)
    grouped = cosine_show_user_list(row_df, date_str)

    if not grouped.empty:
        cosine_show_group_graph(grouped, save_folder)
    cosine_show_bottom()


from .comp_ro1_dashboard_self_sim import (
    self_show_top_sentence,
    self_show_metric,
    self_show_graph,
    self_show_bottom,
)

from funcitons.ro1.macro.self_sim import (
    self_load_data,
    self_calculate_values,
)


def dashboard_self_sim():
    st.title("유저별 행동 유사성 기반 세부 내용")
    date_selector()
    date_str = self_show_top_sentence()
    df = self_load_data(date_str)
    (
        df,
        num_outliers_wide,
        filtered_outliers,
        mean_value,
        median_value,
        Q1,
        Q3,
        IQR,
        num_outliers_wide,
    ) = self_calculate_values(df)
    outliers = self_show_metric(
        df, num_outliers_wide, filtered_outliers, mean_value, median_value, Q1, Q3, IQR
    )
    self_show_graph(df, outliers)
    self_show_bottom(filtered_outliers, Q1, Q3, IQR, num_outliers_wide)


from .comp_ro1_dashboard_graph_image import (
    show_plot_activity_by_minute,
    show_plot_activity_by_second,
    show_plot_activity_by_seconds,
)
from funcitons.ro1.macro.graph_maker import (
    activity_graph_maker,
    get_image_data,
    background_generate,
    image_path_return,
    activity_graph_maker2,
    get_date_range,
    get_csv_download,
    save_download_log
)

import threading
import os, traceback

def dashboard_graph_visualization():
    st.title("행동 유사성 기반 시각화")
    mindate, maxdate = get_date_range()
    st.info(f"입력 가능 일자: {mindate} ~ {maxdate}, 최대 60일")
    st.info("예시) '시작: 2025-05-01', '종료: 2025-05-03 입력시 2025-05-01 00:00:00 ~ 2025-05-02 23:59:59까지 검색합니다.")
    start_date_selector()
    end_date_selector()
    ip_selector()
    
    date_str = str(st.session_state["selected_start_date"])
    end_date_str = str(st.session_state["selected_end_date"])
    selected_ip = str(st.session_state["selected_ip"])

    if not date_str or not end_date_str or not selected_ip:
        st.warning("날짜와 IP를 선택하세요.")
        return
    if st.session_state["selected_start_date"] is not None and st.session_state["selected_end_date"] is not None and st.session_state["selected_ip"] is not None:
        if st.session_state["selected_start_date"] >= st.session_state["selected_end_date"]:
            st.warning("검색 종료 일자가 시작 일자와 같거나 작습니다.")
        else:
            st.success(f"선택된 날짜: {date_str} - {end_date_str}, 선택된 IP: {selected_ip}")
    

        second_image_path, seconds_image_path, minute_image_path = image_path_return(
            date_str, end_date_str, selected_ip
        )

        co1, col2 = st.columns(2)
        with co1:
            show_second = st.checkbox("1초 단위 유저 활동 그래프 보기")
            show_seconds = st.checkbox("10초 단위 유저 활동 그래프 보기")
            show_minute = st.checkbox("1분 단위 유저 활동 그래프 보기")
        with col2:
            reason = st.text_input("다운로드 사유", "매크로 유저 제재 및 근거 확보")
            if st.button("다운로드 데이터 생성 요청",use_container_width=True):
                st.session_state["download_data"] = True
                
            if st.session_state["selected_start_date"] is not None and st.session_state["selected_end_date"] is not None and st.session_state["download"] == False and st.session_state["selected_ip"] is not None and st.session_state["download_data"] == True:
                with st.spinner("다운로드 데이터 생성 중"):
                    st.session_state["download_raw_data"],  st.session_state["download_raw_data_list"] = get_csv_download(date_str, end_date_str, selected_ip)
            if st.session_state["selected_start_date"] is not None and st.session_state["selected_end_date"] is not None and st.session_state["download_data"] == True and st.session_state["selected_ip"] is not None:
                st.session_state["download"] = True
                try:
                    st.download_button("데이터 Excel 다운로드",
                                        st.session_state["download_raw_data"],
                                        file_name = f'{date_str}_{end_date_str}_{selected_ip}.csv',
                                        mime="text/csv",
                                        disabled=not (reason, date_str, end_date_str, selected_ip),
                                        use_container_width=True,)
                except Exception as e:
                    st.error(traceback.print_exc())
                    st.error("검색 시작 일자, 검색 종료 일자, IP, 다운로드 사유 중 입력되지 않은 값이 있습니다.")
                    st.session_state["download_data"] = False
                    st.session_state["download"] = False

            if st.session_state["download"] == True and st.session_state["download_data"] == True:
                save_download_log(st.session_state["download_raw_data_list"], reason)
                st.success("CSV 파일 다운로드 완료")
            
        # 초 단위 그래프 요청
        if show_second:
            if os.path.exists(second_image_path):
                show_plot_activity_by_second(second_image_path)
            elif not st.session_state.graph_generating["second"]:
                with st.spinner("1초 단위 그래프 생성 중..."):
                    df = get_image_data(date_str, end_date_str, selected_ip)
                    st.info("(1/3)데이터 조회 완료")
                    if df is not None:
                        activity_graph_maker2(df, second_image_path, date_str, end_date_str, 1)
                        st.info("(3/3)그래프 생성 완료")
                    else:
                        st.error("입력하신 정보로 조회된 데이터가 없습니다.")
                show_plot_activity_by_second(second_image_path)
            else:
                st.info("1초 단위 그래프 생성 중입니다...")

        st.write("---")

        # 10초 단위 그래프 요청
        if show_seconds:
            if os.path.exists(seconds_image_path):
                show_plot_activity_by_seconds(seconds_image_path)
            elif not st.session_state.graph_generating["seconds"]:
                with st.spinner("10초 단위 그래프 생성 중..."):
                    df = get_image_data(date_str, end_date_str, selected_ip)
                    st.info("(1/3)데이터 조회 완료")
                    if df is not None:
                        activity_graph_maker2(df, seconds_image_path, date_str, end_date_str, 10)
                        st.info("(3/3)그래프 생성 완료")
                    else:
                        st.error("입력하신 정보로 조회된 데이터가 없습니다.")
                show_plot_activity_by_second(seconds_image_path)
            else:
                st.info("10초 단위 그래프 생성 중입니다...")

        st.write("---")
        # 분 단위 그래프 요청
        if show_minute:
            if os.path.exists(minute_image_path):
                show_plot_activity_by_minute(minute_image_path)
            elif not st.session_state.graph_generating["minute"]:
                with st.spinner("1분 단위 그래프 생성 중..."):
                    df = get_image_data(date_str, end_date_str, selected_ip)
                    st.info("(1/3)데이터 조회 완료")
                    if df is not None:
                        activity_graph_maker2(df, minute_image_path, date_str, end_date_str, 60)
                        st.info("(3/3)그래프 생성 완료")
                    else:
                        st.error("입력하신 정보로 조회된 데이터가 없습니다.")
                show_plot_activity_by_minute(minute_image_path)
            else:
                st.info("1분 단위 그래프 생성 중입니다...")

        st.write("---")

        st.subheader("(초단위)위 그래프에 중복 줍기가 발생한 경우 다른 색깔 표기")
