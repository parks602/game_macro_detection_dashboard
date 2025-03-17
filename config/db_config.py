from dotenv import load_dotenv
import os


# 101서버 DB 중 itemlog DB에 연결하기 위한 환경변수를 가져온다.
def itemlog_db_environment_variables():
    load_dotenv()
    server = os.getenv("Datamining_DB_SERVER")
    port = os.getenv("Datamining_DB_PORT")
    database = os.getenv("Datamining_DB_DATABASE")
    username = os.getenv("Datamining_DB_USERNAME")
    password = os.getenv("Datamining_DB_PASSWORD")
    return server, port, database, username, password


# 101서버 DB 중 pdu_db에 연결하기 위한 환경변수를 가져온다.
def pdu_db_environment_variables():
    load_dotenv()
    server = os.getenv("Datamining_DB_SERVER")
    port = os.getenv("Datamining_DB_PORT")
    database = os.getenv("Datamining_streamilt_DB_DATABASE")
    username = os.getenv("Datamining_streamilt_DB_USERNAME")
    password = os.getenv("Datamining_streamilt_DB_PASSWORD")
    return server, port, database, username, password


# 101서버 DB 중 datamining_db에 연결하기 위한 환경변수를 가져온다.
def datamining_db_environment_variables():
    load_dotenv()
    server = os.getenv("Datamining_DB_SERVER")
    port = os.getenv("Datamining_DB_PORT")
    database = os.getenv("Datamining_DB_SELECT_DATABASE")
    username = os.getenv("Datamining_DB_SELECT_USERNAME")
    password = os.getenv("Datamining_DB_SELECT_PASSWORD")
    return server, port, database, username, password


# 172서버 누적로그 DB 연결을 위한 환경변수를 가져온다.
def ItemLog_down_db_environment_variables():
    load_dotenv()
    server = os.getenv("ItemLog_DB_SERVER")
    port = os.getenv("ItemLog_DB_PORT")
    database = os.getenv("ItemLog_DB_DATABASE")
    username = os.getenv("ItemLog_DB_USERNAME")
    password = os.getenv("ItemLog_DB_PASSWORD")
    return server, port, database, username, password
