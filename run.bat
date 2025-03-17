echo 작업 시작

@echo off

REM 가상환경 활성화
call "C:\Users\pdu_admin\Desktop\projects\RO1_Dashboard_with_streamlit\.venv\Scripts\activate"

REM DB 데이터 저장
python "C:\Users\pdu_admin\Desktop\source_v0.0.1\source_v0.0.1\src\datamaker.py"
python "C:\Users\pdu_admin\Desktop\source_v0.0.1\source_v0.0.1\src\data_collector.py"

REM 가상환경 비활성화
deactivate

echo 작업 완료
pause