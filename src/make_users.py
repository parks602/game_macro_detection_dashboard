# register_user_script.py

import argparse
from login_functions import register_user


def main():
    # argparse로 명령줄 인자 받기
    # ArgumentParser 객체 생성: 프로그램 설명과 명령어 인자 설정
    parser = argparse.ArgumentParser(description="Register a new user")

    # 4개의 인자 추가: username, password, email, role
    # 각각의 인자에 대한 설명과 타입을 지정
    parser.add_argument("username", type=str, help="Username for the new user")
    parser.add_argument("password", type=str, help="Password for the new user")
    parser.add_argument("email", type=str, help="Email for the new user")
    parser.add_argument("role", type=str, help="dashboard role, ex) admin, user")

    # 명령줄에서 받은 인자 파싱
    args = parser.parse_args()

    # register_user 함수 호출하여, 받은 인자들을 사용하여 사용자 등록
    register_user(args.username, args.password, args.email, args.role)


# 메인 함수가 실행되도록 설정
if __name__ == "__main__":
    main()

# 사용 방법:
# 이 스크립트는 명령줄에서 실행하여 새 사용자를 등록합니다.
#
# 명령줄에서 실행하는 방법:
# python register_user_script.py <username> <password> <email>
#
# 예시:
# python register_user_script.py testuser Test123! testuser@example.com
#
# 위와 같이 3개의 인자를 입력하여 실행하면,
# 해당 인자들이 register_user 함수에 전달되어 새 사용자 등록이 진행됩니다.
# 이때, 사용자명, 비밀번호, 이메일이 순서대로 전달되어야 합니다.
# 이후, 사용자 등록 결과는 데이터베이스에 저장됩니다.
