import pyodbc
from sqlalchemy import create_engine
import logging
import pandas as pd

from funcitons.config_reader import (
    pdu_db_environment_variables,
    datamining_db_environment_variables,
)

# 로깅 설정
logging.basicConfig(
    filename="ui_database.log",
    format="DataMining, %(asctime)s - %(levelname)s - %(message)s",  # 로그 메시지 형식 설정
    level=logging.INFO,  # 기본 레벨을 INFO로 설정 (INFO 이상의 레벨은 모두 로깅됨)
)

logger = logging.getLogger(__name__)  # 로깅 객체 생성


class Getdata:
    def __init__(self, server, port, database, username, password):
        self.server = server
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
        )
        self.conn = None
        self.engine = None

    def connect_to_db(self):
        try:
            # pyodbc 연결
            self.conn = pyodbc.connect(self.connection_string)
            self.engine = create_engine(
                f"mssql+pyodbc://{self.username}:{self.password}@{self.server}:{self.port}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
            )
            logger.info("Connection successful.")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            self.conn = None
            self.engine = None

    def disconnect_from_db(self):
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database.")
        else:
            logger.warning("No active connection to close.")

    def get_one_fetch(self, query):
        """
        주어진 SQL 쿼리를 사용하여 데이터를 조회하고 첫 번째 결과를 반환합니다.

        Args:
            query (str): 실행할 SQL 쿼리.

        Returns:
            tuple: 쿼리 실행 결과 중 첫 번째 행.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Exception as e:
            logger.error(f"Failed to fetch data with query '{query}': {e}")
            return None

    def get_all_fetch(self, query):
        """
        주어진 SQL 쿼리를 사용하여 데이터를 조회하고 모든 결과를 반환합니다.

        Args:
            query (str): 실행할 SQL 쿼리.

        Returns:
            list: 쿼리 실행 결과.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Failed to fetch data with query '{query}': {e}")
            return None

    def insert_with_execute(self, query):
        """
        주어진 SQL 쿼리를 사용하여 데이터를 삽입합니다.

        Args:
            query (str): 실행할 SQL 쿼리.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            logger.info("✅ Data inserted successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to insert data: {e}")

    def get_df(self, query):
        """
        주어진 SQL 쿼리를 사용하여 데이터를 조회하고 DataFrame으로 반환합니다.

        Args:
            query (str): 실행할 SQL 쿼리.

        Returns:
            pd.DataFrame: 쿼리 실행 결과를 담은 DataFrame.
        """
        if not self.conn:
            logger.error("No active connection. Please connect to the database first.")
            return None
        try:
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data with query '{query}': {e}")
            return None
        
def setup_activity():
    """
    주어진 데이터베이스 유형에 맞는 연결을 설정합니다.

    Returns:
        Getdata: 연결된 데이터베이스 객체.
    """

    server, port, database, username, password = pdu_db_environment_variables()
    activity = Getdata(server, port, database, username, password)
    activity.connect_to_db()
    return activity


def setup_activity_datamining():
    """
    주어진 데이터베이스 유형에 맞는 연결을 설정합니다.

    Returns:
        Getdata: 연결된 데이터베이스 객체.
    """

    server, port, database, username, password = datamining_db_environment_variables()
    activity = Getdata(server, port, database, username, password)
    activity.connect_to_db()
    return activity
