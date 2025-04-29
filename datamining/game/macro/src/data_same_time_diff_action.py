import pandas as pd
import warnings
from db_functions import setup_activity, load_query
from data_logger import logger

warnings.simplefilter("ignore", UserWarning)


class DiffActionProcessor:
    """
    멀티클라이언트 다른행동 - 동일한 시간에 다른 액션을 수행한 사용자 추출 클래스
    """

    def __init__(
        self,
        yesterday: str,
        db_type: str = "datamining_row",
        query_name: str = "get_daily_user_activity_action_all",
        table_name: str = "macro_user_same_time_diff_action_detail",
    ):
        """
        클래스 초기화

        Args:
            yesterday (str): 분석할 날짜 (형식: 'YYYY-MM-DD')
            db_type (str): 데이터베이스 타입 (예: 'itemlog', 'pdu')
            query_name (str): SQL 쿼리 이름 (기본값: 'get_daily_user_activity_action_all')
            table_name (str): 테이블 이름 (기본값: 'macro_user_same_time_diff_action_detail')
        """
        self.db_type = db_type
        self.yesterday = yesterday
        self.query_name = query_name
        self.table_name = table_name

    def fetch_user_activity(self) -> pd.DataFrame:
        """
        주어진 날짜에 대한 사용자 활동 데이터를 데이터베이스에서 조회합니다.

        Returns:
            pd.DataFrame: 사용자 활동 데이터를 담은 DataFrame.
        """
        logger.info(f"Fetching user activity for {self.yesterday}")
        try:
            query = load_query(self.query_name)
            activity = setup_activity(db_type=self.db_type)
            df = activity.get_df(query.format(date=self.yesterday))
            activity.disconnect_from_db()
            logger.info(
                f"Successfully fetched {len(df)} rows of data for {self.yesterday}"
            )
            return df
        except Exception as e:
            logger.error(f"Failed to fetch user activity for {self.yesterday}: {e}")
            raise

    def filter_diff_actions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        IP와 logtime을 기준으로 다중 액션과 srcAccountID를 가진 사용자 데이터를 필터링합니다.

        Args:
            df (pd.DataFrame): 사용자 활동 데이터.

        Returns:
            pd.DataFrame: 필터링된 사용자 활동 데이터.
        """
        logger.info(
            "Filtering users with multiple actions and different account IDs at the same time"
        )
        df.drop(columns=["SID"], inplace=True)  # sid 컬럼 삭제
        grouped = df.groupby(["IP", "logtime"]).filter(lambda x: len(x) > 1)
        result = grouped.groupby(["IP", "logtime"]).filter(
            lambda x: x["action"].nunique() > 1 and x["srcAccountID"].nunique() > 1
        )
        result = result.groupby("srcAccountID").filter(lambda x: len(x) > 10)
        result = result.drop_duplicates()
        logger.info(f"Filtered data, {len(result)} rows remaining")
        return result

    def insert_filtered_data(self, result: pd.DataFrame):
        """
        필터링된 데이터를 데이터베이스에 삽입합니다.

        Args:
            result (pd.DataFrame): 삽입할 필터링된 데이터.
        """
        logger.info(f"Inserting filtered data for {self.yesterday}")
        try:
            result["Date"] = self.yesterday
            activity = setup_activity("pdu")
            activity.insert_dataframe_replace_date(self.table_name, result)
            activity.disconnect_from_db()
            logger.info(
                f"Successfully inserted {len(result)} rows of filtered data for {self.yesterday}"
            )
        except Exception as e:
            logger.error(f"Failed to insert filtered data for {self.yesterday}: {e}")
            raise

    def make_diff_action_data(self):
        """
        메소드 (fetch_user_activity, filter_diff_actions, insert_filtered_data)를 순차적으로 실행하여 데이터를 처리합니다.
        Returns:
            pd.DataFrame: 처리된 데이터.
        """
        logger.info(
            f"Processing data for users with different actions at the same time for {self.yesterday}"
        )
        try:
            df = self.fetch_user_activity()
            result = self.filter_diff_actions(df)
            self.insert_filtered_data(result)
            logger.info(f"Successfully processed data for {self.yesterday}")
        except Exception as e:
            logger.error(f"Failed to process data for {self.yesterday}: {e}")
            raise
