from dotenv import load_dotenv
import os


# 환경 변수를 한 번만 로드
def load_environment_variables():
    load_dotenv()


# 특정 DB에 연결하기 위한 환경변수를 가져오는 함수
def get_db_environment_variables(db_type):
    """
    db_type에 따라 해당 DB의 환경 변수를 가져옵니다.

    :param db_type: DB의 종류 ('itemlog', 'pdu', 'datamining')
    :return: (server, port, database, username, password)
    """
    load_environment_variables()

    # 환경 변수 로드
    if db_type == "itemlog":
        server = os.getenv("ITEMLOG_DB_SERVER")
        port = os.getenv("ITEMLOG_DB_PORT")
        database = os.getenv("ITEMLOG_DB_DATABASE")
        username = os.getenv("ITEMLOG_DB_USERNAME")
        password = os.getenv("ITEMLOG_DB_PASSWORD")
    elif db_type == "pdu":
        server = os.getenv("PDU_DB_SERVER")
        port = os.getenv("PDU_DB_PORT")
        database = os.getenv("PDU_DB_DATABASE")
        username = os.getenv("PDU_DB_USERNAME")
        password = os.getenv("PDU_DB_PASSWORD")
    elif db_type == "datamining":
        server = os.getenv("DATAMINING_DB_SERVER")
        port = os.getenv("DATAMINING_DB_PORT")
        database = os.getenv("DATAMINING_DB_DATABASE")
        username = os.getenv("DATAMINING_DB_USERNAME")
        password = os.getenv("DATAMINING_DB_PASSWORD")
    elif db_type == 'datamining_row':
        server = os.getenv("DATAMINING_LOWDB_SERVER")
        port = os.getenv("DATAMINING_LOWDB_PORT")
        database = os.getenv("DATAMINING_LOWDB_DATABASE")
        username = os.getenv("DATAMINING_LOWDB_USERNAME")
        password = os.getenv("DATAMINING_LOWDB_PASSWORD")    
    else:
        raise ValueError(f"Unknown db_type: {db_type}")

    return server, port, database, username, password
