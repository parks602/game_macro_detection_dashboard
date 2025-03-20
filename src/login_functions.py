import pyodbc
import bcrypt
import re
import random
from datetime import datetime, timedelta
import requests
import httpx
import sys, os
import socket
import platform
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.db_config import pdu_db_environment_variables
from config.api_config import load_api_environment_variables


def get_db_connection():
    server, port, database, username, password = pdu_db_environment_variables()
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
    )
    return conn


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def register_user(username: str, password: str, email: str, role: str):
    now = datetime.now()
    print(username, email)
    """사용자 계정 등록 (이메일 추가)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO users (username, password_hash, email, role, last_password_change, created_at) VALUES (?, ?, ?, ?, ?, ?)"
    query2 = "INSERT INTO password_reset_codes (username, email) VALUES (?, ?)"
    try:
        # 아이디 중복 체크
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print("이미 등록된 ID입니다.")
            return False, "이미 등록된 ID입니다."

        # 이메일 중복 체크
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print("이미 등록된 이메일입니다.")
            return False, "이미 등록된 이메일입니다."

        # 비밀번호 해싱
        hashed_pw = hash_password(password)

        cursor.execute(query, (username, hashed_pw, email, role, now, now))
        cursor.execute(query2, (username, email))
        conn.commit()
        print("사용자 등록 완료")
        return True, "사용자 등록 완료"
    except pyodbc.IntegrityError as e:
        conn.rollback()
        print("데이터 무결성 오류 발생:", e)

    finally:
        cursor.close()
        conn.close()


def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 해당 사용자 조회
    cursor.execute(
        "SELECT password_hash, last_password_change, role FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "로그인 정보가 틀립니다.", False  # 계정이 존재하지 않음
    # 비밀번호 검증
    if not bcrypt.checkpw(password.encode(), user[0].encode()):
        return False, "로그인 정보가 틀립니다.", False  # 비밀번호 오류

    # 비밀번호 변경 여부 확인
    if user[1] + timedelta(days=180) < datetime.now():
        return (
            False,
            "비밀번호를 변경한 지 180일이 지났습니다. 비밀번호 변경이 필요합니다.",
            False,
        )

    return True, "로그인 성공", user[2]  # 로그인 성공


def validate_password(password: str) -> str:
    # 최소 8자리
    if len(password) < 8:
        return "비밀번호는 최소 8자 이상이어야 합니다."

    # 대문자 체크
    if len(re.findall(r"[A-Z]", password)) == 0:
        return "비밀번호는 최소 1개의 대문자를 포함해야 합니다."

    # 소문자 체크
    if len(re.findall(r"[a-z]", password)) == 0:
        return "비밀번호는 최소 1개의 소문자를 포함해야 합니다."

    # 숫자 체크
    if len(re.findall(r"\d", password)) == 0:
        return "비밀번호는 최소 1개의 숫자를 포함해야 합니다."

    # 특수문자 체크
    if len(re.findall(r"[^\w\s]", password)) == 0:
        return "비밀번호는 최소 1개의 특수문자를 포함해야 합니다."

    return "valid"  # 비밀번호가 모든 규칙을 만족할 경우


# 비밀번호 변경
def change_password(username, old_password, new_password, new_password_retype):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 기존 비밀번호 확인
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user or not bcrypt.checkpw(old_password.encode(), user[0].encode()):
        conn.close()
        return False, "기존 로그인 정보가 틀립니다"

    # 비밀번호 정책 검증
    if old_password == new_password:
        conn.close()
        return False, "새로운 비밀번호는 기존 비밀번호와 다르게 설정해주세요."

    if new_password != new_password_retype:
        conn.close()
        return False, "새 비밀번호와 재입력 비밀번호가 일치하지 않습니다."

    # 비밀번호 정책 검증
    validation_message = validate_password(new_password)
    if validation_message != "valid":
        conn.close()
        return False, validation_message

    hashed_new_pw = hash_password(new_password)

    # 비밀번호 변경
    cursor.execute(
        "UPDATE users SET password_hash = ?, last_password_change = GETDATE() WHERE username = ?",
        (hashed_new_pw, username),
    )
    conn.commit()
    conn.close()
    return True, "비밀번호가 성공적으로 변경되었습니다."


def generate_reset_code():
    return str(random.randint(100000, 999999))


def send_message_id(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
    username = cursor.fetchone()
    if username:  # 값이 존재하는 경우
        username = username[0]
    url = "https://api.dooray.com/common/v1/members"

    # 쿼리 파라미터 설정
    params = {
        "externalEmailAddresses": f"{email}",  # 이메일을 여기에 추가
        "page": 0,
        "size": 20,
    }
    API_TOKEN = load_api_environment_variables()

    headers = {
        "Authorization": f"dooray-api {API_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, params=params)

    # 응답 확인
    if response.status_code == 200:
        user_num = response.json()["result"][0]["id"]
    else:
        return (response.status_code, response.text)

    body = f"가입하신 아이디\n {username}"

    try:
        send_message(
            headers,
            user_num,
            body,
        )
        return True, "아이디가 메신저로 전송됐습니다."
    except Exception as e:
        return False, f"메신저 전송에 실패했습니다. 오류: {e}"


def send_reset_code(username, email):
    """인증 코드 메신저 발송"""
    reset_code = str(random.randint(100000, 999999))  # 6자리 랜덤 코드 생성
    create_time = datetime.now()
    expiry_time = datetime.now() + timedelta(minutes=10)  # 만료 시간 10분 후
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, email FROM users WHERE username = ? and email = ?",
        (username, email),
    )
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False, "사용자 정보가 존재하지 않습니다."
    username = user[0]
    email = user[1]
    # 인증 코드와 만료시간 DB에 저장
    cursor.execute(
        "UPDATE password_reset_codes SET reset_code = ?, create_time = ?, reset_expiry = ? WHERE username = ?",
        (reset_code, create_time, expiry_time, username),
    )
    conn.commit()
    conn.close()

    url = "https://api.dooray.com/common/v1/members"

    # 쿼리 파라미터 설정
    params = {
        "externalEmailAddresses": f"{email}",  # 이메일을 여기에 추가
        "page": 0,
        "size": 20,
    }
    API_TOKEN = os.getenv("API_TOKEN")
    headers = {
        "Authorization": f"dooray-api {API_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, params=params)

    # 응답 확인
    if response.status_code == 200:
        try:
            user_num = response.json()["result"][0]["id"]
        except IndexError:
            return False, "등록된 사용자가 없습니다."
    else:
        return (response.status_code, response.text)

    body = f"인증 코드: {reset_code}\n이 코드는 10분간 유효합니다."

    try:
        send_message(
            headers,
            user_num,
            body,
        )
        return True, "인증 코드가 메신저로로 전송되었습니다."
    except Exception as e:
        return False, f"메신저 전송에 실패했습니다. 오류: {e}"


def send_message(headers, user_number, message):
    api_url = "https://api.dooray.com/messenger/v1/channels/direct-send"

    params = {"text": f"{message}", "organizationMemberId": f"{user_number}"}

    response = requests.post(api_url, headers=headers, json=params)

    if response.status_code == 200:
        print("메시지 전송 성공!")
    else:
        print("메시지 전송 실패:", response.text)


def change_user_password(username, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 인증 코드 검증
    cursor.execute(
        "SELECT reset_code FROM password_reset_codes WHERE username = ?", (username,)
    )
    result = cursor.fetchone()

    if not result:
        conn.close()
        return "존재하지 않는 사용자입니다."

    validate_password_result = validate_password(new_password)
    if validate_password_result != "valid":
        return validate_password_result

    # 비밀번호 해싱 후 업데이트
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hashed_password, username),
    )
    conn.commit()
    conn.close()

    return "비밀번호 변경 완료!"


def verify_reset_code(username=None, email=None, reset_code=None):
    """인증 코드가 유효한지 확인"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if username is not None and email is None:
        cursor.execute(
            "SELECT reset_code, reset_expiry FROM password_reset_codes WHERE username = ?",
            (username,),
        )
        result = cursor.fetchone()
        conn.close()
    elif email is not None and username is None:
        cursor.execute(
            "SELECT reset_code, reset_expiry FROM password_reset_codes WHERE email = ?",
            (email,),
        )
        result = cursor.fetchone()
        conn.close()
    if result:
        stored_code, expiry_time = result
        if stored_code == reset_code and expiry_time > datetime.now():
            print("인증 코드 확인 완료")
            return True
        else:
            print("인증 코드 만료")
    return False


# def get_client_ip():
#    response = requests.get("https://api64.ipify.org?format=json")
#    return response.json()["ip"]
def get_client_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


def get_user_agent():
    # headers = httpx.get("https://httpbin.org/get").json()["headers"]
    # return headers.get("User-Agent", "Unknown")
    return f"Python/{sys.version.split()[0]} ({platform.system()} {platform.release()})"

def check_login_attempt(username):
    now = datetime.now()
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"""
    SELECT blocked_time FROM users WHERE username = '{username}'
    """
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result is None or result[0] is None:
        return True
    elif result[0] > now:
        return False
    else:
        return True
        
def check_fail_login(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"""SELECT TOP (10) status
      FROM login_logs
      where username = '{username}' 
      order by login_time DESC"""
    cursor.execute(query)
    statuses = [row[0] for row in cursor.fetchall()]
    fail_count = 0

    for status in statuses:
        if status == 'failure':
            fail_count +=1
        else:
            break

    if fail_count == 10:
        query = f"""UPDATE users SET blocked_time = DATEADD(MINUTE, 30, GETDATE"()) WHERE username  = '{username}'"""
        conn.commit()
        cursor.close()
        conn.close()
        return False, _
    else:
        return True, fail_count
    
def log_login_attempt(username, status, ip_address="unknown", user_agent="unknown"):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO login_logs (username, login_time, status, ip_address, user_agent)
    VALUES (?, GETDATE(), ?, ?, ?)
    """
    cursor.execute(query, (username, status, ip_address, user_agent))

    conn.commit()
    cursor.close()
    conn.close()


def find_id_function(email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    if result:
        return True, f"아이디는 {result[0]} 입니다."
    else:
        return False, "해당 이메일로 등록된 사용자가 없습니다."
