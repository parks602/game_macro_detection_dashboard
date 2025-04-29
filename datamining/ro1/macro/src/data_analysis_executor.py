from data_same_time_diff_action import DiffActionProcessor
from data_self_similarity import SelfSimilarityProcessor
from data_cosine_similarity import cosine_data_maker
from data_collector import collect_data
from data_logger import logger
from datetime import datetime, timedelta
import os
import sys

def main() -> None:
    """
    메인 실행 함수로, 전체 데이터 처리 파이프라인을 순차적으로 실행합니다.

    Args:
        None

    Returns:
        None
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    save_folder = os.path.join(
        project_root, "result", "graph", yesterday[:4], yesterday[5:7], yesterday[8:10]
    )
    try:
        processor = DiffActionProcessor(yesterday=yesterday)
        processor.make_diff_action_data()
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
    try:
        processor = SelfSimilarityProcessor(yesterday=yesterday)
        processor.make_self_sim_data()
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
    try:
        cosine_data_maker(yesterday, save_folder)
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
    try:
        collect_data(yesterday)
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)

# 메인 함수 실행
if __name__ == "__main__":
    main()
