from dotenv import load_dotenv
import os


# .env 파일을 한 번만 로드하는 함수
def load_environment_variables():
    """
    환경 변수를 한 번만 로드합니다.
    """
    load_dotenv()


# 두레이 API 토큰을 가져오는 함수
def load_api_token():
    """
    .env 파일에서 두레이 API 토큰(API_TOKEN)을 로드하여 반환합니다.
    :return: str: API 토큰
    """
    # 환경 변수 로드
    load_environment_variables()

    # API 토큰 가져오기
    token = os.getenv("API_TOKEN")
    if not token:
        raise ValueError("API_TOKEN is not set in the .env file.")
    return token
