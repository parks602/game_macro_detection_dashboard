echo �۾� ����

@echo off

REM ����ȯ�� Ȱ��ȭ
call "C:\Users\pdu_admin\Desktop\projects\RO1_Dashboard_with_streamlit\.venv\Scripts\activate"

cd "C:\Users\pdu_admin\Desktop\project\datamining\ro1\macro\src"
REM DB ������ ����
python "data_analysis_executor.py"

REM ����ȯ�� ��Ȱ��ȭ
deactivate

echo �۾� �Ϸ�
pause