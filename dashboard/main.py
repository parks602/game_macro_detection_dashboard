import subprocess
from dotenv import load_dotenv
import sys
import os

# 현재 파일의 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")
)  # ui 경로 추가

# .env 파일 로드
load_dotenv()
print(f"📂 현재 작업 디렉토리: {os.getcwd()}")
subprocess.run(["streamlit", "run", "ui/page_main.py"])
