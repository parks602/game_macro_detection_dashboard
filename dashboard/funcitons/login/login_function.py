import re
import bcrypt
from datetime import datetime, timedelta
import socket
import sys
import platform
from funcitons.db_connector import setup_activity
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit import runtime

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
    return True, 'valid'  # 비밀번호가 모든 규칙을 만족할 경우


def check_input(username, password):
    if not username:
        return "사용자 이름을 입력하세요."
    if not password:
        return "비밀번호를 입력하세요."
    return True


def check_login_attempt(username, client):
    now = datetime.now()
    query = f"""SELECT blocked_time FROM users WHERE username = '{username}'
    """
    result = client.get_one_fetch(query)
    if result is None or result[0] is None:
        return True
    elif result[0] > now:
        return "로그인 횟수 초과로 로그인 시도 차단 중입니다."
    else:
        return True


def validate_input_and_password(username, password, client):
    check_input_message = check_input(username, password)
    if check_input_message != True:
        return check_input_message

    check_password_message = validate_password(password)
    if check_password_message != True:
        return check_password_message

    check_block_message = check_login_attempt(username, client)
    if check_block_message != True:
        return check_block_message
    return True


def get_db_connection():
    return setup_activity()


def authenticate(username, password, client):
    """
    사용자 인증을 처리합니다.
    성공하면 True와 함께 역할 정보를 반환하고, 실패하면 False와 메시지를 반환합니다.
    """
    query = (
        f"SELECT password_hash, last_password_change, role FROM users WHERE username = '{username}'")
    user = client.get_one_fetch(query)
    if not user:
        return False, "로그인 정보가 틀립니다."  # 계정이 존재하지 않음
    # 비밀번호 검증
    if not bcrypt.checkpw(password.encode(), user[0].encode()):
        return False, "로그인 정보가 틀립니다."  # 비밀번호 오류

    # 비밀번호 변경 여부 확인
    if user[1] + timedelta(days=180) < datetime.now():
        return False, "비밀번호를 변경한 지 180일이 지났습니다. 비밀번호 변경이 필요합니다."
    
    return True, str(user[2]) # 로그인 성공


def authenticate_system(username, password, client):
    success, login_message = authenticate(username, password, client)
    if success == True:
        log_login_attempt(username, "success", client)
    else:
        log_login_attempt(username, "failure", client)
    return success, login_message


def log_login_attempt(username, status, client):
    """
    로그인 시도 후, 성공 여부를 기록합니다.
    """
    ip, agent = get_sys_info()
    query = """INSERT INTO login_logs (username, login_time, status, ip_address, user_agent)
            VALUES (?, GETDATE(), ?, ?, ?)"""
    values = [username, status, ip, agent]
    client.insert_login_with_execute(query, values)


def get_sys_info():
    """
    시스템 정보를 가져옵니다.
    """
    return get_client_ip(), get_user_agent()


def get_client_ip():
    """
    클라이언트 IP 주소를 가져옵니다.

    Returns:
        str: 클라이언트 IP 주소
    """
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None
        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None
    return session_info.request.remote_ip


def get_user_agent():
    """
    사용자 에이전트 정보를 가져옵니다.

    Returns:
        str: 사용자 에이전트 정보
    """
    return f"Python/{sys.version.split()[0]} ({platform.system()} {platform.release()})"


def check_fail_login(username, client):
    query = f"""SELECT TOP (10) status
      FROM login_logs
      where username = '{username}' 
      order by login_time DESC"""
    statuses = [row[0] for row in client.get_all_fetch(query)]
    fail_count = 0

    for status in statuses:
        if status == "failure":
            fail_count += 1
        else:
            break

    if fail_count == 10:
        query = f"""UPDATE users SET blocked_time = DATEADD(MINUTE, 30, GETDATE"()) WHERE username  = '{username}'"""
        client.insert_with_execute(query)
        return False
    else:
        return True


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()
