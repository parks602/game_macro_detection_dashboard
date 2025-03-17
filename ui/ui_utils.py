import streamlit as st


def configure_streamlit():
    st.set_page_config(
        page_title="RO1 DashBoard", page_icon="./UI/icon/gravity.ico", layout="wide"
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
