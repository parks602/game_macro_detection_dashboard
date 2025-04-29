from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import pandas as pd
from data_logger import logger
from db_functions import setup_activity, load_query
from pathlib import Path
import matplotlib.pyplot as plt
import plotly.express as px

class CosineProcessor:
    """
    사용자간 코사인 유사도를 계산하고 클러스터링 하는 클래스
    """

    def __init__(
        self,
        db_type: str,
        yesterday: str,
        query_name: str = "get_daily_user_activity_action_one",
        table_name: str = "macro_user_cosine_similarity",
        threshold: float = 0.99,
        session_threshold: pd.Timedelta = pd.Timedelta(
            minutes=2
        ),  # pd.Timedelta로 타입 명시
    ):
        """
        클래스 초기화

        Args:
            db_type (str): 데이터베이스 타입 (예: 'itemlog', 'pdu')
            yesterday (str): 분석할 날짜 (형식: 'YYYY-MM-DD')
            query_name (str): SQL 쿼리 이름 (기본값: 'get_daily_user_activity_action_all')
            table_name (str): 테이블 이름 (기본값: 'macro_user_self_similarity')
            threshold (float): 유사도 임계값 (기본값: 0.99)
            session_threshold (pd.Timedelta): 유저 세션 시간 임계값 (기본값: 2분)
        """
        self.db_type = db_type
        self.yesterday = yesterday
        self.query_name = query_name
        self.table_name = table_name
        self.threshold = threshold
        self.session_threshold = session_threshold

    def update_db_type(self, db_type: str):
        """
        db_type 값을 변경하는 메소드

        Args:
            db_type: (str): 새로운 디비 연결 타입
        """
        self.db_type = db_type

    def update_table(self, table_name: str):
        """
        table_name 값을 변경하는 메소드

        Args:
            table_name: (str): 새로운 테이블명
        """
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
            self.df_row = df
            activity.disconnect_from_db()
            logger.info(
                f"Successfully fetched {len(df)} rows of data for {self.yesterday}"
            )
            return df
        except Exception as e:
            logger.error(f"Failed to fetch user activity for {self.yesterday}: {e}")
            raise

    def detect_sessions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        유저별로 세션을 감지하여 세션 정보를 DataFrame으로 반환

        Args:
            df (pd.DataFrame): 유저 활동 로그 데이터 (srcAccountID, logtime 포함)

        Returns:
            pd.DataFrame: 유저별 세션 정보 (srcAccountID, Session_Number, Start_Time, End_Time)
        """
        logger.info(f"Detecting user activite sessions for {self.yesterday}")
        SRC_ACCOUNT_ID = "srcAccountID"
        LOGTIME = "logtime"
        DF_SESSION_COLUMNS = [
            "srcAccountID",
            "Session_Number",
            "Start_Time",
            "End_Time",
        ]
        records = []
        try:
            for user_id, group in df.groupby(SRC_ACCOUNT_ID):
                group = group.sort_values(LOGTIME).reset_index(drop=True)
                session_number = 0
                start_time = group.loc[0, LOGTIME]
                end_time = group.loc[0, LOGTIME]

                for i in range(1, len(group)):
                    current_time = group.loc[i, LOGTIME]

                    # 새로운 세션 감지
                    if (current_time - end_time) > self.session_threshold:
                        session_number += 1
                        records.append([user_id, session_number, start_time, end_time])
                        start_time = current_time

                    # 접속 종료 시간 갱신
                    end_time = current_time

            df_session = pd.DataFrame(records, columns=DF_SESSION_COLUMNS)
            logger.info(f"Detected {self.yesterday} user activity sessions")
            return df_session

        except Exception as e:
            logger.error(f"Failed to detect user activity sessions: {e}")
            raise

    def create_user_timelines(self, df_session: pd.DataFrame) -> dict:
        """
        하루 24시간을 기준으로 유저별 접속 상태 타임라인을 생성

        Args:
            df_session (pd.DataFrame): 유저별 세션 정보 (srcAccountID, Session_Number, Start_Time, End_Time 포함)

        Returns:
            dict: 유저별 접속 상태 타임라인 (user_id: timeline)
        """
        logger.info(f"Creating user timelines for {self.yesterday}")
        SRC_ACCOUNT_ID = "srcAccountID"
        START_TIME = "Start_Time"
        END_TIME = "End_Time"
        SECOND_IN_DAY = 24 * 60 * 60  # 하루 24시간을 초 단위로 타임라인 생성
        try:
            # 접속 상태 타임라인 초기화
            user_timelines = {
                user: np.zeros(SECOND_IN_DAY, dtype=int)
                for user in df_session[SRC_ACCOUNT_ID].unique()
            }

            # 각 세션에 대해 타임라인을 업데이트
            for _, row in df_session.iterrows():
                user = row[SRC_ACCOUNT_ID]
                start_time = row[START_TIME]
                end_time = row[END_TIME]

                # 세션 동안의 타임라인 값 업데이트 (1로 설정)
                start_sec = int(
                    (start_time - pd.Timestamp(start_time.date())).total_seconds()
                )
                end_sec = int(
                    (end_time - pd.Timestamp(end_time.date())).total_seconds()
                )

                user_timelines[user][start_sec:end_sec] = 1
            logger.info(f"Created user timelines for {self.yesterday}")
            return user_timelines
        except Exception as e:
            logger.error(f"Failed to create user timelines: {e}")
            raise

    def calculate_cosine_similarity(self, user_timelines: dict) -> np.ndarray:
        """
        유저들의 접속 상태 타임라인을 기반으로 코사인 유사도 행렬을 계산하고
        상삼각행렬 값을 추출하여 반환

        Args:
            user_timelines (dict): 유저별 접속 상태 타임라인 (user_id: timeline)

        Returns:
            np.ndarray: 유사도 행렬의 상삼각행렬 (중복되지 않은 유사도 값)
        """
        logger.info(f"Calculating cosine similarity for {self.yesterday}")
        try:
            # 타임라인 배열 변환
            timelines_array = np.array(list(user_timelines.values()))
            user_ids = list(user_timelines.keys())

            # 코사인 유사도 계산
            similarity_matrix = cosine_similarity(timelines_array)
            logger.info("Similarity matrix complete")

            # 상삼각행렬 추출 (중복되지 않는 유사도 값만 추출)
            similarities = similarity_matrix[
                np.triu_indices_from(similarity_matrix, k=1)
            ]
            logger.info(f"Calculated cosine similarity for {self.yesterday}")
            return similarity_matrix, similarities, user_ids
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            raise

    def find_connected_groups(
        self, user_ids: list, similarity_matrix: np.ndarray
    ) -> dict:
        """
        유사도 행렬을 기반으로 연결된 유저 그룹을 찾는 메소드 (그래프 사용하지 않음)

        Args:
            user_ids (list): 유저 ID 목록
            similarity_matrix (np.ndarray): 유저 간 코사인 유사도 행렬

        Returns:
            dict: 2명 이상 포함된 그룹별 유저 목록 (Group n: [user1, user2, ...])
        """
        logger.info(f"Finding connected groups for {self.yesterday}")
        try:
            # 유저 ID 인덱스 매핑 (user_id -> index)
            user_id_to_idx = {user_id: idx for idx, user_id in enumerate(user_ids)}

            # 방문 여부 체크 (배열로 처리하여 속도 최적화)
            visited = np.zeros(len(user_ids), dtype=bool)

            def dfs(user_id, group):
                """
                DFS 방식으로 연결된 유저를 찾고 그룹에 추가

                Args:
                    user_id (int): 현재 유저 ID
                    group (set): 현재 그룹에 속한 유저들
                """
                # 현재 유저 방문 표시
                user_idx = user_id_to_idx[user_id]
                visited[user_idx] = True
                group.append(user_id)  # 리스트에 유저 추가

                # 현재 유저와 다른 유저 간 유사도 확인
                for i, other_user_id in enumerate(user_ids):
                    if (
                        i != user_idx
                        and not visited[i]
                        and similarity_matrix[user_idx][i] >= self.threshold
                    ):
                        dfs(other_user_id, group)

            groups = []
            for user_id in user_ids:
                if not visited[user_id_to_idx[user_id]]:
                    group = []
                    dfs(user_id, group)
                    groups.append(group)

            # 2명 이상 포함된 그룹만 필터링
            self.grouped_users = {
                f"Group {i+1}": group
                for i, group in enumerate(groups)
                if len(group) > 1
            }
            logger.info(f"Found connected groups for {self.yesterday}")
        except Exception as e:
            logger.error(f"Failed to find connected groups: {e}")
            raise

    def make_macro_suer_cosine_simiarity_data(
        self, yesterday: str, user_ids: list):
        """
        매크로 유저 그룹 데이터를 저장하는 메소드.

        Args:
            yesterday (str): 저장할 날짜
            user_ids (list): 전체 유저 ID 목록
            grouped_users (dict): 그룹별 유저 목록

        Returns:
            None
        """
        result = {key: len(value) for key, value in self.grouped_users.items()}
        TABLE_COLUMNS = [
            "Date",
            "All_user",
            "All_group",
            "Multi_user_group",
            "Multi_user_group_all_user",
        ]
        logger.info("Make cosine_similarity_data...")
        try:
            # 다중 유저 그룹 필터링
            two_or_more_items = {
                key: value for key, value in self.grouped_users.items() if len(value) >= 2
            }

            # 저장할 데이터 구성
            data = {
                TABLE_COLUMNS[0]: [yesterday],  # 날짜
                TABLE_COLUMNS[1]: [len(user_ids)],  # 전체 유저 수
                TABLE_COLUMNS[2]: [len(result)],  # 전체 그룹 수
                TABLE_COLUMNS[3]: [len(two_or_more_items)],  # 다중 유저 그룹 수
                TABLE_COLUMNS[4]: [
                    sum(
                        len(value)
                        for value in self.grouped_users.values()
                        if len(value) >= 2
                    )
                ],  # 다중 유저 그룹의 총 유저 수
            }

            save_df = pd.DataFrame(data)
            return save_df
        except Exception as e:
            logger.error(f"Failed to make cosine_similarity_data: {e}")
            raise

    def save_macro_suer_cosine_simiarity_data(self, save_df: pd.DataFrame) -> None:
        """
        매크로 유저 그룹 데이터를 저장하는 메소드.

        Args:
            save_df (pd.DataFrame): 저장할 데이터가 담긴 DataFrame

        Returns:
            None
        """
        logger.info("Inserting macro_user_groups into database...")
        try:
            # DB 연결 초기화 및 데이터 저장
            activity = setup_activity(db_type=self.db_type)
            activity.insert_dataframe_replace_date(self.table_name, save_df)
            activity.disconnect_from_db()
            logger.info("Macro user groups data saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save cosine_similarity_data: {e}")
            raise

    def make_cosine_similarity_histogram_data(
        self, yesterday: str, similarities: np.ndarray
    ):
        """
        코사인 유사도 히스토그램 데이터를 생성하는 메소드

        Args:
            yesterday (str): 어제 날짜 (형식: "YYYY-MM-DD")
            similarities (np.ndarray): 유사도 배열

        Returns:
            pd.DataFrame: 히스토그램 데이터
        """
        logger.info("Making cosine similarity histogram data...")
        TABLE_COLUMNS = ["Date", "Range_Start", "Range_End", "Count"]
        try:
            # 유사도 분포 히스토그램 데이터 생성
            bins = np.linspace(0, 1, 11)
            counts, bin_edges = np.histogram(similarities, bins=bins)

            # DataFrame 생성
            range_histogram = pd.DataFrame(
                {
                    TABLE_COLUMNS[0]: [yesterday] * len(counts),
                    TABLE_COLUMNS[1]: bin_edges[:-1],
                    TABLE_COLUMNS[2]: bin_edges[1:],
                    TABLE_COLUMNS[3]: counts,
                }
            )
            logger.info(f"Cosine similarity histogram data created {self.yesterday}")
            return range_histogram
        except Exception as e:
            logger.error(f"Failed to make cosine similarity histogram data: {e}")
            raise

    def save_cosine_similarity_histogram_data(
        self, range_histogram: pd.DataFrame
    ) -> None:
        """
        코사인 유사도 히스토그램 데이터를 저장하는 메소드

        Args:
            range_histogram (pd.DataFrame): 히스토그램 데이터

        Returns:
            None
        """
        logger.info("Inserting cosine similarity histogram data into database...")
        try:
            # DB 연결 초기화 및 데이터 저장
            activity = setup_activity(db_type=self.db_type)
            activity.insert_dataframe_replace_date(self.table_name, range_histogram)
            activity.disconnect_from_db()
            logger.info(
                f"Cosine similarity histogram data saved successfully. {self.yesterday}"
            )
        except Exception as e:
            logger.error(f"Failed to save cosine similarity histogram data: {e}")
            raise

    def get_analysis_keys(self):
        """2명 이상의 유저가 포함된 그룹 키 리스트 반환"""
        return [key for key, value in self.grouped_users.items() if len(value) > 1]

    def get_filtered_df(self, key_name):
        """
        특정 그룹의 유저들만 필터링

        Args:
            key_name (str): 그룹 키 이름

        Returns:
            pd.DataFrame: 필터링된 데이터
        """
        analysis_users = self.grouped_users[key_name]
        return self.df_row[self.df_row["srcAccountID"].isin(analysis_users)]

    def calculate_logtime_counts(self, filtered_df):
        """
        각 srcAccountID별 logtime 총 개수 계산

        Args:
            filtered_df (pd.DataFrame): 필터링된 데이터

        Returns:
            pd.DataFrame: srcAccountID별 logtime 총 개수
        """
        return (
            filtered_df.groupby("srcAccountID")["logtime"]
            .count()
            .reset_index(name="Total_logtime_Count")
        )

    def merge_on_logtime(self, filtered_df):
        """logtime을 기준으로 자기 자신과 병합"""
        return pd.merge(filtered_df, filtered_df, on=["logtime"], suffixes=("_x", "_y"))

    def get_mismatch_counts(self, merged_df):
        """서로 다른 srcAccountID이면서 SID 또는 MapName이 다른 경우 중복 카운트 계산"""
        filtered_df2 = merged_df[
            merged_df["srcAccountID_x"] != merged_df["srcAccountID_y"]
        ]
        return (
            filtered_df2.groupby("srcAccountID_x")["logtime"]
            .nunique()
            .reset_index(name="Duplication_count")
        ), filtered_df2

    def get_unique_ips(self, src_account_id, filtered_df2):
        """srcAccountID별 고유 IP 목록 생성"""
        ips_x = set(
            filtered_df2[filtered_df2["srcAccountID_x"] == src_account_id][
                "IP_x"
            ].unique()
        )
        ips_y = set(
            filtered_df2[filtered_df2["srcAccountID_y"] == src_account_id][
                "IP_y"
            ].unique()
        )
        return list(ips_x.union(ips_y))

    def process_group(self, key_name):
        """단일 그룹을 분석하여 결과 생성"""
        filtered_df = self.get_filtered_df(key_name)
        logtime_counts = self.calculate_logtime_counts(filtered_df)
        merged_df = self.merge_on_logtime(filtered_df)
        mismatch_counts, filtered_df2 = self.get_mismatch_counts(merged_df)

        result = (
            pd.merge(
                logtime_counts,
                mismatch_counts,
                how="left",
                left_on="srcAccountID",
                right_on="srcAccountID_x",
            )
            .drop(columns=["srcAccountID_x"])
            .fillna(0)
        )

        result["Duplication_count"] = result["Duplication_count"].astype(int)
        result["Ratio"] = result["Duplication_count"] / result["Total_logtime_Count"]
        result["IPs"] = result["srcAccountID"].apply(
            lambda x: self.get_unique_ips(x, filtered_df2)
        )
        result.insert(0, "Date", self.yesterday)
        result.insert(2, "Group_name", key_name)

        return result

    def make_macro_user_cosine_simiarity_detail_data(self):
        """유저간 유사도 기반 매크로 유저 그룹 상세 데이터 생성"""
        try:
            logger.info("Make cosine_similarity_detail_data...")
            results = [self.process_group(key) for key in self.get_analysis_keys()]
            final_df = pd.concat(results, ignore_index=True)
            final_df["IPs"] = final_df["IPs"].apply(str)
            return final_df
        except Exception as e:
            logger.error(f"Failed to make cosine_similarity_detail_data: {e}")
            raise

    def save_macro_user_cosine_simiarity_detail_data(self, final_df: pd.DataFrame):
        """
        유저간 유사도 기반 매크로 유저 그룹 상세 데이터 저장

        Args:
            final_df (pd.DataFrame): 저장할 데이터가 담긴 DataFrame

        Returns:
            None
        """
        try:
            logger.info(
                "Inserting macro_user_cosine_similarity_detail into database..."
            )
            activity = setup_activity(db_type=self.db_type)
            activity.insert_dataframe_replace_date(self.table_name, final_df)
            activity.disconnect_from_db()
            logger.info("Macro user cosine similarity detail data saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save cosine_similarity_detail_data: {e}")
            raise

    # 그룹별 유저 접속 시간 그래프 생성
    def make_user_activity_grapgh(self, df, save_folder):
        try:
            logger.info(
                "Start make user activity graph...")
            plt.rcParams["font.family"] = "Malgun Gothic"
            two_or_more_items = {
                key: value for key, value in self.grouped_users.items() if len(value) >= 2
            }
            sample_data = sorted(two_or_more_items.items(), key=lambda x: len(x[1]))

            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            # top_5_groups에 대해 그래프 생성
            for group_name, user_list in sample_data:
                # 해당 그룹의 접속 기록 데이터를 모은 리스트
                group_data = []

                # 각 유저별 접속 시간 데이터를 group_data 리스트에 추가
                for user_id in user_list:
                    user_data = df[df["srcAccountID"] == user_id]

                    for _, row in user_data.iterrows():
                        start_time = row["Start_Time"]
                        end_time = row["End_Time"]
                        group_data.append(
                            {"AID": user_id, "start_time": start_time, "end_time": end_time}
                        )

                # group_data를 DataFrame으로 변환
                group_df = pd.DataFrame(group_data)

                # plotly.express로 간트 차트 생성
                fig = px.timeline(
                    group_df.sort_values(by="AID").reset_index(drop=True),
                    x_start="start_time",
                    x_end="end_time",
                    y="AID",
                    title=f"{group_name} User Active Times",
                    labels={"AID": "AID", "start_time": "Login Start", "end_time": "Login End"},
                )
                min_time = pd.Timestamp(group_df["start_time"].dt.date.min()).replace(
                    hour=0, minute=0, second=0
                )
                max_time = min_time + pd.Timedelta(days=1)
                # 레이아웃 설정
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title="AID",
                    yaxis_type="category",  # 범주형 y축
                    showlegend=False,  # 범례 숨기기
                    xaxis_range=[min_time, max_time],
                    width=1200,  # 그래프의 가로 크기
                    height=600,
                )
                # 그래프 저장
                image_path = os.path.join(
                    save_folder, f"{group_name}_access_gantt_chart_plotly.png"
                )
                fig.write_image(image_path)
            logger.info(
                "Finish make user activity graph...")
        except Exception as e:
            logger.error(f"Failed to make graph image: {e}")
            raise
        
    def make_histogram(self, save_folder, similarities):
        try:
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            logger.info(
                "Start make all user histogram graph...")
            plt.hist(similarities, bins=50, color="blue", edgecolor="black")
            plt.title("Cosine Similarity Distribution")
            plt.xlabel("Cosine Similarity")
            plt.ylabel("Frequency")
            plt.savefig(
                "%s/all_user_histogram.png" % (save_folder),
                dpi=300,
                bbox_inches="tight",
            )
            logger.info(
                "Finish make all user histogram graph...")
        except Exception as e:
            logger.error(f"Failed to make graph image: {e}")
            raise
        
def cosine_data_maker(yesterday, save_folder):
    logger.info("Cosine data START")
    processer = CosineProcessor(db_type="datamining_row", yesterday=yesterday)
    
    # ItemLog DB에서 어제 날짜의 사용자 활동 데이터를 가져옵니다.
    df_row = processer.fetch_user_activity()
    
    # 사용자 활동 데이터를 필터링합니다.
    df_session = processer.detect_sessions(df_row)
    
    # 사용자 활동 데이터를 기반으로 유저별 접속 상태 타임라인을 생성합니다.
    user_timelines = processer.create_user_timelines(df_session)

    # 유저들의 접속 상태 타임라인을 기반으로 코사인 유사도 행렬을 계산하고 상삼각행렬 값을 추출합니다.
    similarity_matrix, similarities, user_ids = processer.calculate_cosine_similarity(user_timelines)


    processer.make_histogram(save_folder, similarities)
    # 유사도 행렬을 기반으로 연결된 유저 그룹을 찾습니다.
    processer.find_connected_groups(user_ids, similarity_matrix)

    # 'macro_suer_cosine_simiarity' 테이블 저장용 매크로 유저 그룹 데이터 생성
    save_df = processer.make_macro_suer_cosine_simiarity_data(
        processer.yesterday, user_ids
    )

    # 데이터 저장을 위한 클래스 테이블명, db_type 변경
    processer.update_table("macro_user_cosine_similarity")
    processer.update_db_type("pdu")

    # 'macro_suer_cosine_simiarity' 테이블에 매크로 유저 그룹 데이터 저장
    processer.save_macro_suer_cosine_simiarity_data(save_df)

    # 'make_cosine_similarity_histogram' 테이블 저장용 코사인 유사도 히스토그램 데이터 생성
    range_histogram = processer.make_cosine_similarity_histogram_data(
        processer.yesterday, similarities
    )

    # 데이터 저장을 위한 클래스 테이블명 변경
    processer.update_table("cosine_similarity_histogram")

    # 'make_cosine_similarity_histogram' 테이블에 코사인 유사도 히스토그램 데이터 저장
    processer.save_cosine_similarity_histogram_data(range_histogram)


    # 'macro_user_cosine_similarity_detail' 테이블 저장용 매크로 유저 그룹 상세 데이터 생성
    final_df = processer.make_macro_user_cosine_simiarity_detail_data()

    # 데이터 저장을 위한 클래스 테이블명 변경
    processer.update_table("macro_user_cosine_similarity_detail")

    # 'macro_user_cosine_similarity_detail' 테이블에 매크로 유저 그룹 상세 데이터 저장
    processer.save_macro_user_cosine_simiarity_detail_data(final_df)
    
    os.makedirs(save_folder, exist_ok = True)

    processer.make_user_activity_grapgh(df = df_session, save_folder = save_folder)
