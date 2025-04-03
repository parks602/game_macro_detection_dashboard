import random
from datetime import datetime, timedelta
import requests
import bcrypt
import os
from .login_function import validate_password
import streamlit as st


def send_reset_code(username, email, client):
    reset_code = str(random.randint(100000, 999999))
    create_time = datetime.now().replace(microsecond=0)
    expiry_time = create_time + timedelta(minutes=10)

    if not check_user_info(username, email, client):
        return False, "사용자 정보가 존재하지 않습니다."
    update_reset_code(reset_code, create_time, expiry_time, username, client)
    try:
        checker, message =  message_sender(email, reset_code)
        return checker, message
    except:
        return False, "message_sender 오류"


def check_user_info(username, email, client):
    query = f"SELECT username, email FROM users WHERE username = '{username}' and email = '{email}'"
    user = client.get_one_fetch(query)
    if not user:
        return False
    else:
        return True


def update_reset_code(reset_code, create_time, expiry_time, username, client):
    query = f"UPDATE password_reset_codes SET reset_code = '{reset_code}', create_time = '{create_time}', reset_expiry = '{expiry_time}' WHERE username = '{username}'"
    client.insert_with_execute(query)


def message_sender(email, reset_code):
    try:
        url = "https://api.dooray.com/common/v1/members"
    except:
        return False, "url 오류"

    # 쿼리 파라미터 설정
    try:
        params = {
            "externalEmailAddresses": f"{email}",  # 이메일을 여기에 추가
            "page": 0,
            "size": 20,
        }
    except:
        return False, "param 오류"
    try:
        API_TOKEN = os.getenv("API_TOKEN")
        headers = {
            "Authorization": f"dooray-api {API_TOKEN}",
            "Content-Type": "application/json",
        }
    except:
        return False, "os env 오류"
    try:
        response = requests.get(url, headers=headers, params=params)
    except:
        return False, "request 오류"

    # 응답 확인
    if response.status_code == 200:
        try:
            user_num = response.json()["result"][0]["id"]
        except IndexError:
            return False, "입력하신 정보에 일치하는 두레이 사용자가 없습니다."
    else:
        return response.status_code, response.text

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


def verify_reset_code(username, resetcode, client):
    query = f"SELECT reset_code, reset_expiry FROM password_reset_codes WHERE username = '{username}'"
    result = client.get_one_fetch(query)
    if result != None:
        stored_code, expiry_time = result
        if expiry_time < datetime.now():
            return "인증 코드가 만료되었습니다."
        elif stored_code != resetcode:
            return "인증 코드 올바르지 않습니다."
        else:
            return True
    else:
        return "쿼리가 안됐습니다"


def change_user_password(username, new_password, client):
    query = f"SELECT reset_code FROM password_reset_codes WHERE username = '{username}'"
    result = client.get_one_fetch(query)
    if not result:
        return "존재하지 않는 사용자입니다."
    success, validation_message = validate_password(new_password)
    if success != True:
        return validation_message
    # 비밀번호 해싱 후 업데이트
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    try:
        change_time = datetime.now().replace(microsecond=0)
        query = f"UPDATE users SET password_hash = '{hashed_password}', last_password_change = '{change_time}' WHERE username = '{username}'"
        client.insert_with_execute(query)
        return True
    except:
        return "쿼리 오류"
