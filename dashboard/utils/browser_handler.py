import os
import jwt
import uuid
from datetime import datetime, timedelta
import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_local_storage import LocalStorage


def cookie_load_environment_variables():
    load_dotenv()
    secret_key = os.getenv("COOKIES_PASSWORD")
    return secret_key

def jwt_load_environment_variables():
    load_dotenv()
    secret_key = os.getenv("JWT_SECRET")
    return secret_key

class cookieAuth:
    def __init__(self):
        self.secret_key = cookie_load_environment_variables()
        self.cookie_manager = EncryptedCookieManager(
            prefix="dashboard/streamlit-cookies-manager/",
            password=self.secret_key,
        )

    def check_cookie_ready(self):
        if not self.cookie_manager.ready():
            st.stop()

    def clear_all_cookies(self):
        self.check_cookie_ready()
        for cname in list(self.cookie_manager.keys()):
            self.cookie_manager[cname] = ""
            del self.cookie_manager[cname]
        self.cookie_manager.save()
        st.rerun()
        
    def clear_cookie_auth(self):
        for cname in list(self.cookie_manager.keys()):
            del self.cookie_manager[cname]
        self.cookie_manager.save()
        

    def save_login_to_cookie(self, username, role):
        auth_handler = AuthManager()
        token = auth_handler.create_jwt_token(username, role)
        payload = auth_handler.verify_jwt_token(token)
        self.cookie_manager["token_auth"] = token
        self.cookie_manager["username"] = username
        self.cookie_manager["role"] = role
        self.cookie_manager.save()

        st.session_state['token_auth'] = token

    def load_login_from_cookie(self):
        token = self.cookie_manager.get("token_auth", None)
        if token:
            auth_handler = AuthManager()
            payload = auth_handler.verify_jwt_token(token)
            if payload:              
                st.session_state.update(
                    {
                        "authenticated": True,
                        "user_name": payload.get("username"),
                        "role": payload.get("role"),
                        "token_auth": token,
                    }
                )
                return True
        return False

    def load_one_cookie(self, key):
        return self.cookie_manager.get(key, None)


class AuthManager:
    def __init__(self, secret_key=None):
        self.secret_key = jwt_load_environment_variables()
        self.algorithm = "HS256"
        self.session_hours = 1  # 1시간 세션

    def create_jwt_token(self, username, role, page_state=None):
        """JWT 토큰 생성"""
        utc_now = datetime.utcnow()
        payload = {
            "username": username,
            "role": role,
            "exp": utc_now + timedelta(hours=self.session_hours),
            "iat": utc_now,
            "page_state": page_state or {},
            "jti": str(uuid.uuid4()),  # 토큰 ID 추가
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_jwt_token(self, token):
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("ExpiredSignatureError")
            return None
        except jwt.InvalidSignatureError:
            print("InvalidSinatureError")
            return None
        except jwt.DecodeError:
            print("DecodeError")
            return None
        except jwt.InvalidKeyError:
            print("InvalidKeyError")
            return None
        except jwt.InvalidTokenError as e:
            print(f"InvalidTokenError, {str(e)}")
            return None
        


class LocalStorageManager:
    def __init__(self):
        self.local_storage = LocalStorage()

    def get_item(self, key):
        return self.local_storage.getItem(key)

    def set_item(self, key, value):
        self.local_storage.setItem(key, value)

    def clear(self):
        self.local_storage.deleteAll()


def initialize_session_state(cookie_manager, local_storage):
    """쿠키 정보를 먼저 확인하고 세션 상태 초기화"""

    # 기본 세션 상태 정의
    session_defaults = {
        "token_auth": None,
        "cookie_auth": None,
        "error": False,
        "authenticated": False,
        "language": 'kr',
        "change_step": None,
        "reset_step": None,
        "user_name": None,
        "reset_username": None,
        "role": None,
        "page": None,
        "selected_page": None,
        "admin_selected_page": None,
        "macro_date": None,
        "user_aid": None,
        "selected_tab": "로그인",
        "selected_ip": None,
        "selected_start_date": None,
        "selected_end_date": None,
        "graph_generating": {
            "second": False,
            "minute": False,
            "seconds": False,
        },
    }

    # 쿠키에서 로그인 정보 로드 시도
    auth_info = {}
    if cookie_manager:
        auth_info = cookie_manager.load_login_from_cookie()
        
    for key, default_value in session_defaults.items():
        st.session_state[key] = default_value

    if local_storage:
        try:
            language_setting = local_storage.get_item("language")
            if language_setting is not None:
                session_defaults["language"] =  language_setting
            else:
                session_defaults["language"] = 'kr'
        except:
            pass
    if cookie_manager:
        cookie_manager.load_login_from_cookie()
