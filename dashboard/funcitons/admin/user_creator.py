from datetime import datetime
import pyodbc
from funcitons.login.login_function import get_db_connection, hash_password


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
