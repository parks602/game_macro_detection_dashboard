import pandas as pd
from db_functions import setup_activity
from data_logger import logger
from queries import GET_DAILY_USER_ACTIVITY_ALL_ACTION


class DataProcessor:
    """
    데이터를 처리하고 필터링하는 클래스입니다.
    주어진 날짜에 대한 유저 액션 데이터를 필터링하여 반환합니다.
    """

    def __init__(self, db_type: str):
        """
        데이터베이스 연결을 설정합니다.

        Args:
            db_type (str): 사용할 데이터베이스의 종류
        """
        self.db_type = db_type
        self.activity = setup_activity(db_type=self.db_type)

    def fetch_data(self, yesterday: str) -> pd.DataFrame:
        """
        주어진 날짜에 대해 데이터를 가져옵니다.

        Args:
            yesterday (str): 가져올 데이터의 날짜 (형식: "YYYY-MM-DD")

        Returns:
            pd.DataFrame: 쿼리 결과로 반환된 데이터프레임
        """
        df = self.activity.get_df(
            GET_DAILY_USER_ACTIVITY_ALL_ACTION.format(date=yesterday)
        )
        if df is None or df.empty:
            logger.warning(f"No data found for {yesterday}")
            return None
        return df[["IP", "logtime", "action", "srcAccountID"]]

    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        'IP'와 'logtime'이 같고 'action'과 'srcAccountID'가 다른 데이터를 필터링합니다.

        Args:
            df (pd.DataFrame): 필터링할 데이터프레임

        Returns:
            pd.DataFrame: 필터링된 데이터프레임
        """
        grouped = df.groupby(["IP", "logtime"]).filter(lambda x: len(x) > 1)
        result = grouped.groupby(["IP", "logtime"]).filter(
            lambda x: x["action"].nunique() > 1 and x["srcAccountID"].nunique() > 1
        )
        result = result.groupby("srcAccountID").filter(lambda x: len(x) > 10)
        result = result.drop_duplicates()
        return result

    def insert_data(self, result: pd.DataFrame, yesterday: str):
        """
        처리된 데이터를 pdu DB에 삽입합니다.

        Args:
            result (pd.DataFrame): 삽입할 데이터
            yesterday (str): 데이터의 날짜 정보
        """
        result["Date"] = yesterday
        self.activity.insert_dataframe_replace_date(
            "macro_user_same_time_diff_action_detail", result
        )
        self.activity.disconnect_from_db()
