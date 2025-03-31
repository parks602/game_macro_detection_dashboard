from .data_same_time_diff_action import DiffActionProcessor
from .data_self_similarity import SelfSimilarityProcessor

# from data_collector import collect_data
from datetime import datetime, timedelta
import logging
import os

# 로깅 설정
logging.basicConfig(
    filename="data_mining.log",
    format="DataMining, %(asctime)s - %(levelname)s - %(message)s",  # 로그 메시지 형식 설정
    level=logging.INFO,  # 기본 레벨을 INFO로 설정 (INFO 이상의 레벨은 모두 로깅됨)
)

logger = logging.getLogger(__name__)  # 로깅 객체 생성


def main() -> None:
    """
    메인 실행 함수로, 전체 데이터 처리 파이프라인을 순차적으로 실행합니다.

    Args:
        None

    Returns:
        None
    """
    project_root = os.path.abspath(os.path.dirname(__file__))
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
        processor.make_self_similarity_data()
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)


# 메인 함수 실행
if __name__ == "__main__":
    main()
