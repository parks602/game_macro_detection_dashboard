import streamlit as st


def configure_streamlit():
    st.set_page_config(
        page_title="Gravity DashBoard",
        page_icon="asset//icon/gravity.ico",
        layout="wide",
    )

    st.markdown(
        """
            <style>
                   .block-container {
                        padding-top: 2rem;
                        padding-bottom: 1rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
            <style>
                .big-font {
                    font-size:25px !important;
                }
            </style>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <style>
        /* 우측 상단 점 3개 메뉴 숨기기 */
        .css-1lcbm6t {
            visibility: hidden;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
