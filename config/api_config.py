from dotenv import load_dotenv
import os


# .env 파일에서 API_TOKEN을 가져오는 함수
# 두레이 API를 사용하기 위한 토큰을 가져온다.
def load_api_environment_variables():
    load_dotenv()
    token = os.getenv("API_TOKEN")
    return token
