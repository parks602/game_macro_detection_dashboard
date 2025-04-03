import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
from db_functions import setup_activity, load_query
from data_logger import logger
import warnings

warnings.simplefilter("ignore", UserWarning)


class SelfSimilarityProcessor:
    """
    사용자별 자기 유사도를 계산하고 처리하는 클래스
    """

    def __init__(
        self,
        yesterday: str,
        db_type: str = 'pdu',
        query_name: str = "get_daily_user_activity_action_all",
        table_name: str = "macro_user_self_similarity",
    ):
        """
        클래스 초기화

        Args:
            db_type (str): 데이터베이스 타입 (예: 'itemlog', 'pdu')
            yesterday (str): 분석할 날짜 (형식: 'YYYY-MM-DD')
            query_name (str): SQL 쿼리 이름 (기본값: 'get_daily_user_activity_action_all')
            table_name (str): 테이블 이름 (기본값: 'macro_user_self_similarity')
        """
        self.db_type = db_type
        self.yesterday = yesterday
        self.query_name = query_name
        self.table_name = table_name

    def fetch_user_activity(self) -> pd.DataFrame:
        """
        주어진 날짜에 대한 사용자 활동 데이터를 데이터베이스에서 조회합니다.

        Args:
            yesterday (str): 분석할 날짜 (YYYY-MM-DD).

        Returns:
            pd.DataFrame: 사용자 활동 데이터를 담은 DataFrame.
        """
        logger.info(f"Fetching user activity for {self.yesterday}")
        try:
            query = load_query(self.query_name)
            activity = setup_activity(db_type="datamining_row")
            df = activity.get_df(query.format(date=self.yesterday))
            activity.disconnect_from_db()
            logger.info(
                f"Successfully fetched {len(df)} rows of data for {self.yesterday}"
            )
            return df
        except Exception as e:
            logger.error(f"Failed to fetch user activity for {self.yesterday}: {e}")
            raise

    def filter_valid_users(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        유효한 사용자만 필터링하여 반환합니다. (logtime 단위 갯수(1분)가 10 이상인 사용자)

        Args:
            df (pd.DataFrame): 사용자 활동 데이터.

        Returns:
            pd.DataFrame: 유효한 사용자만 필터링된 데이터.
        """
        logger.info("Filtering valid users with at least 10 samples per minute")
        df["logtime"] = pd.to_datetime(df["logtime"])
        df.set_index("logtime", inplace=True)
        logtime_counts = df.groupby("srcAccountID").resample("min").action.count()
        valid_users = logtime_counts.groupby("srcAccountID").count()
        valid_users = valid_users[valid_users >= 10].index
        filtered_df = df[df["srcAccountID"].isin(valid_users)]
        logger.info(f"Filtered down to {len(filtered_df)} valid users")
        return filtered_df

    def calculate_self_similarity(self, user_df: pd.DataFrame) -> pd.Series:
        """
        주어진 유저에 대해 자기 유사도를 계산합니다.

        Args:
            user_df (pd.DataFrame): 사용자별 데이터.

        Returns:
            pd.Series: 계산된 코사인 유사도 및 자기 유사도를 포함한 시리즈.
        """
        logger.info(
            f"Calculating self-similarity for {user_df['srcAccountID'].iloc[0]}"
        )
        action_counts = (
            user_df.resample("min").action.value_counts().unstack(fill_value=0)
        )
        action_counts = action_counts.loc[(action_counts != 0).any(axis=1)]
        cosine_similarities = []

        for i in range(1, len(action_counts)):
            vec1 = action_counts.iloc[i - 1].values.reshape(1, -1)
            vec2 = action_counts.iloc[i].values.reshape(1, -1)
            similarity = cosine_similarity(vec1, vec2)[0, 0]
            cosine_similarities.append(similarity)

        avg_cosine_similarity = (
            np.mean(cosine_similarities) if cosine_similarities else 0
        )
        sigma = np.std(cosine_similarities) if cosine_similarities else 0

        self_sim = 1 - 0.5 * sigma if avg_cosine_similarity != 0 else 0.5
        logtime_count = len(action_counts)

        return pd.Series(
            {
                "cosine_similarity": round(avg_cosine_similarity, 4),
                "self_similarity": round(self_sim, 4),
                "logtime_count": logtime_count,
            }
        )

    def insert_self_similarity_data(self, result: pd.DataFrame):
        """
        계산된 자기 유사도 데이터를 데이터베이스에 삽입합니다.

        Args:
            result (pd.DataFrame): 계산된 자기 유사도 데이터.
        """
        logger.info(f"Inserting self-similarity data for {self.yesterday}")
        try:
            result["Date"] = self.yesterday
            activity = setup_activity("pdu")
            activity.insert_dataframe_replace_date(self.table_name, result)
            activity.disconnect_from_db()
            logger.info(
                f"Successfully inserted {len(result)} rows of self-similarity data for {self.yesterday}"
            )
        except Exception as e:
            logger.error(
                f"Failed to insert self-similarity data for {self.yesterday}: {e}"
            )
            raise

    def make_self_sim_data(self):
        """
        자기 유사도 데이터를 처리하고 데이터베이스에 저장합니다.

        Returns:
            pd.DataFrame: 처리된 데이터.
        """
        logger.info(f"Making self-similarity data for {self.yesterday}")
        try:
            df = self.fetch_user_activity()
            df_filtered = self.filter_valid_users(df)
            result = (
                df_filtered.groupby("srcAccountID")
                .apply(self.calculate_self_similarity)
                .reset_index()
            )
            self.insert_self_similarity_data(result)
            logger.info(
                f"Successfully created self-similarity data for {self.yesterday}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create self-similarity data for {self.yesterday}: {e}"
            )
            raise


if __name__ == "__main__":
    pass
