import subprocess
from dotenv import load_dotenv
import sys
import streamlit as st


# .env 파일 로드
load_dotenv()
subprocess.run(["streamlit", "run", "ui/page_main.py"])
