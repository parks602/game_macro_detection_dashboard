import sys, os
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from sqlalchemy import create_engine
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.db_config import (
    itemlog_db_environment_variables,
    pdu_db_environment_variables,
    datamining_db_environment_variables,
    ItemLog_down_db_environment_variables,
)


def setup_activity(db_type):
    if db_type == "itemlog":
        server, port, database, username, password = itemlog_db_environment_variables()
    elif db_type == "pdu":
        server, port, database, username, password = pdu_db_environment_variables()
    elif db_type == "datamining":
        server, port, database, username, password = (
            datamining_db_environment_variables()
        )
    activity = Getdata(server, port, database, username, password)
    activity.connect_to_db()
    return activity


def setup_activity_download(download_date):
    server, port, database, username, password = ItemLog_down_db_environment_variables()
    database = f"{database}_{download_date[:4]}{download_date[6:8]}"
    activity = Getdata(server, port, database, username, password)
    activity.connect_to_db()
    return activity


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def get_df(self, query):
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
        """DataFrame을 MSSQL 테이블에 삽입"""
        if not self.conn:
            logger.error("No active connection. Please connect to the database first.")
            return

        cursor = self.conn.cursor()
        columns = ", ".join(df.columns)
        placeholders = ", ".join(["?" for _ in df.columns])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            # Executing batch insert using executemany for better performance
            data = [tuple(row) for _, row in df.iterrows()]
            cursor.executemany(query, data)

            self.conn.commit()
            logger.info("✅ DataFrame inserted successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to insert DataFrame: {e}")
        finally:
            cursor.close()

    def insert_dataframe_replace_date(self, table_name, df):
        """특정 날짜의 기존 데이터를 삭제하고 새로운 데이터를 삽입"""
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


def update_environment_file():
    # 하루 전 날짜 계산
    yesterday = datetime.now() - timedelta(days=1)
    formatted_date = yesterday.strftime("%Y%m")  # 202502 형식으로
    db_value = f"ItemLog_Baphomet_{formatted_date}"  # "ItemLog_202502" 형식으로

    # .env 파일 경로
    env_file_path = "../.env"

    # .env 파일에서 기존 값을 찾아 업데이트하거나 새로 추가
    with open(env_file_path, "r") as file:
        lines = file.readlines()

    # 기존 값과 비교
    item_log_db_value_exists = False
    for i, line in enumerate(lines):
        if line.startswith("ItemLog_DB_DATABASE"):
            # 기존 값 확인
            current_value = line.split("=")[1].strip()
            if current_value == db_value:
                item_log_db_value_exists = True  # 값이 같으면 갱신하지 않음
                break
            else:
                # 값이 다르면 갱신
                lines[i] = f'ItemLog_DB_DATABASE = "{db_value}"\n'
            break

    if not item_log_db_value_exists:
        # .env 파일을 갱신
        with open(env_file_path, "w") as file:
            file.writelines(lines)

        # 기존 값이 없으면 새로 추가
        if not any(line.startswith("ItemLog_DB_DATABASE") for line in lines):
            with open(env_file_path, "a") as file:
                file.write(f'ItemLog_DB_DATABASE = "{db_value}"\n')


def data_download(selected_aid, down_date, reasons, reason_dict):
    activity = setup_activity_download(down_date)
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        for reason in reasons:
            if reason == "action_diff":
                df = pd.DataFrame()
                df.to_excel(writer, sheet_name=reason_dict[reason], index=False)
            elif reason == "self_sim":
                df = pd.DataFrame()
                df.to_excel(writer, sheet_name=reason_dict[reason], index=False)
            elif reason == "action_one":
                df = pd.DataFrame()
                df.to_excel(writer, sheet_name=reason_dict[reason], index=False)
            elif reason == "cosine_sim":
                df = pd.DataFrame()
                df.to_excel(writer, sheet_name=reason_dict[reason], index=False)
    excel_file.seek(0)
    return excel_file
