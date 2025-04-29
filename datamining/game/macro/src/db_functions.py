import pyodbc
import pandas as pd
from sqlalchemy import create_engine
import logging
import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(
                os.path.abspath(
                    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
                )
            )
        )
    )
)
from common.config.db_config import get_db_environment_variables

# 로깅 설정
logging.basicConfig(
    filename="data_mining.log",
    format="DataMining, %(asctime)s - %(levelname)s - %(message)s",  # 로그 메시지 형식 설정
    level=logging.INFO,  # 기본 레벨을 INFO로 설정 (INFO 이상의 레벨은 모두 로깅됨)
)

logger = logging.getLogger(__name__)  # 로깅 객체 생성


class Getdata:
    """
    데이터베이스와 연결하여 데이터를 가져오거나 삽입하는 클래스.
    """

    def __init__(self, server, port, database, username, password):
        """
        클래스 초기화. 데이터베이스 서버 연결 정보 설정.

        Args:
            server (str): 데이터베이스 서버 주소.
            port (str): 데이터베이스 포트.
            database (str): 데이터베이스 이름.
            username (str): 사용자 이름.
            password (str): 비밀번호.
        """
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
        """
        데이터베이스에 연결합니다.

        연결 성공 시 로그에 메시지를 남기고, 실패 시 오류 메시지를 출력합니다.
        """
        try:
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
        """
        데이터베이스와의 연결을 끊습니다.

        연결이 되어 있지 않으면 경고 메시지를 출력합니다.
        """
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

    def insert_dataframe(self, table_name, df):
        """
        DataFrame을 주어진 테이블에 삽입합니다.

        Args:
            table_name (str): 데이터를 삽입할 테이블 이름.
            df (pd.DataFrame): 삽입할 데이터가 담긴 DataFrame.
        """
        if not self.conn:
            logger.error("No active connection. Please connect to the database first.")
            return

        cursor = self.conn.cursor()
        columns = ", ".join(df.columns)
        placeholders = ", ".join(["?" for _ in df.columns])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            data = [tuple(row) for _, row in df.iterrows()]
            cursor.executemany(query, data)
            self.conn.commit()
            logger.info("✅ DataFrame inserted successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to insert DataFrame: {e}")
        finally:
            cursor.close()

    def insert_dataframe_replace_date(self, table_name, df):
        """
        특정 날짜의 기존 데이터를 삭제하고 새로운 데이터를 삽입합니다.

        Args:
            table_name (str): 데이터를 삽입할 테이블 이름.
            df (pd.DataFrame): 삽입할 데이터가 담긴 DataFrame.
        """
        if not self.conn:
            logger.error("No active connection. Please connect to the database first.")
            return

        cursor = self.conn.cursor()

        # Date 컬럼의 첫 번째 값 (모든 데이터가 동일한 날짜라고 가정)
        target_date = df["Date"].iloc[0]  # Date 컬럼의 첫 번째 값

        columns = ", ".join(df.columns)
        placeholders = ", ".join(["?" for _ in df.columns])

        delete_query = f"DELETE FROM {table_name} WHERE Date = ?"
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            # 1️⃣ 기존 날짜 데이터 삭제
            cursor.execute(delete_query, (target_date,))

            # 2️⃣ 새로운 데이터 삽입 (배치 방식으로 성능 향상)
            data = [tuple(row) for _, row in df.iterrows()]
            cursor.executemany(insert_query, data)

            self.conn.commit()
            logger.info(f"✅ Data for {target_date} replaced successfully")
        except Exception as e:
            logger.error(f"❌ Insert failed: {e}")
        finally:
            cursor.close()


def setup_activity(db_type):
    """
    주어진 데이터베이스 유형에 맞는 연결을 설정합니다.

    Args:
        db_type (str): 'itemlog', 'pdu', 또는 'datamining' 중 하나의 데이터베이스 유형.

    Returns:
        Getdata: 연결된 데이터베이스 객체.
    """

    server, port, database, username, password = get_db_environment_variables(db_type)
    activity = Getdata(server, port, database, username, password)
    activity.connect_to_db()
    return activity


def load_query(query_name: str) -> str:
    """
    SQL 파일에서 특정 쿼리를 불러오는 함수.

    Args:
        query_name (str): 사용할 쿼리의 이름

    Returns:
        str: SQL 쿼리 문자열
    """
    queries_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "queries")
    file_path = os.path.join(queries_dir, query_name + ".sql")
    # 파일이 존재하는지 확인 후 로깅 처리
    if not os.path.exists(file_path):
        logger.error(f"Query file '{file_path}' not found.")
        return None  # 예외 발생 대신 None 반환

    # 파일 읽기
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            lines = file.readlines()
            cleaned_lines = [line.split("--")[0].strip() for line in lines if not line.strip().startswith("--")]
            query = " ".join(cleaned_lines)
            return query.strip()
    except Exception as e:
        logger.error(f"Error reading SQL file '{file_path}': {e}")
        return None


if __name__ == "__main__":
    pass
