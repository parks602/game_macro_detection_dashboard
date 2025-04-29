import bcrypt
from .login_function import validate_password
import os
import sys
from funcitons.db_connector import setup_activity


def change_password(username, old_password, new_password, new_password_retype, client):
    query = f"""SELECT password_hash
            FROM users
            WHERE username = '{username}'"""
    user = client.get_one_fetch(query)

    if not user or not bcrypt.checkpw(old_password.encode(), user[0].encode()):
        return False, "기존 로그인 정보가 틀립니다"

    # 비밀번호 정책 검증
    if old_password == new_password:
        return False, "새로운 비밀번호는 기존 비밀번호와 다르게 설정해주세요."

    if new_password != new_password_retype:
        return False, "새 비밀번호와 재입력 비밀번호가 일치하지 않습니다."

    # 비밀번호 정책 검증
    success, validation_message = validate_password(new_password)
    if validation_message != "valid":
        return False, validation_message

    hashed_new_pw = hash_password(new_password)

    update_query = (
        f"""UPDATE users
            SET password_hash = '{hashed_new_pw}',
                last_password_change = GETDATE()
            WHERE username = '{username}'"""
        )
    client.insert_with_execute(update_query)
    return True, "비밀번호가 성공적으로 변경되었습니다. 로그인 해주세요."


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()
