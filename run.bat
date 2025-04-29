echo 작업 시작

@echo off

REM 가상환경 활성화
call "C:\Users\pdu_admin\Desktop\projects\RO1_Dashboard_with_streamlit\.venv\Scripts\activate"

cd "C:\Users\pdu_admin\Desktop\project\datamining\ro1\macro\src"
REM DB 데이터 저장
python "data_analysis_executor.py"

REM 가상환경 비활성화
deactivate

echo 작업 완료
pause