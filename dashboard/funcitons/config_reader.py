from dotenv import load_dotenv
import os


# 101서버 DB 중 pdu_db에 연결하기 위한 환경변수를 가져온다.
def pdu_db_environment_variables():
    load_dotenv()
    server = os.getenv("PDU_DB_SERVER")
    port = os.getenv("PDU_DB_PORT")
    database = os.getenv("PDU_DB_DATABASE")
    username = os.getenv("PDU_DB_USERNAME")
    password = os.getenv("PDU_DB_PASSWORD")
    return server, port, database, username, password


def datamining_db_environment_variables():
    load_dotenv()
    server = os.getenv("DATAMINING_DB_SERVER")
    port = os.getenv("DATAMINING_DB_PORT")
    database = os.getenv("DATAMINING_DB_DATABASE")
    username = os.getenv("DATAMINING_DB_USERNAME")
    password = os.getenv("DATAMINING_DB_PASSWORD")
    return server, port, database, username, password
