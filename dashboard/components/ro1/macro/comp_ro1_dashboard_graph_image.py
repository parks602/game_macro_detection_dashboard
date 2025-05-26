import streamlit as st
import os
from datetime import datetime, timedelta


def show_plot_activity_by_second(image_path):
    st.subheader("(1초단위)선택 일자, 기준 IP에서 활동한 AID의 활동 그래프")
    st.image(
        image_path,
        caption="RO1 매크로 활동(1초 단위)",
        use_container_width = True

    )


def show_plot_activity_by_seconds(image_path):
    st.subheader("(10초단위)선택 일자, 기준 IP에서 활동한 AID의 활동 그래프")
    st.image(
        image_path,
        caption="RO1 매크로 활동(1초 단위)",
        use_container_width = True

    )


def show_plot_activity_by_minute(image_path):
    st.subheader("(1분단위)선택 일자, 기준 IP에서 활동한 AID의 활동 그래프")
    st.image(
        image_path,
        caption="RO1 매크로 활동량(1분 단위)",
        use_container_width = True
    )
