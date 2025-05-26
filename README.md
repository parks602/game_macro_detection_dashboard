## 1. 개요

### 프로젝트의 목적 및 기능 개요

이 대시보드는 게임 로그 데이터를 분석하여 특정 행동 패턴을 시각화하고, 매크로 유저를 탐지하는 기능을 제공한다.

### 핵심 기술 스택

사용 기술 스택: `Python, MSSQL`, `Streamlit(UI)`, `Matplotlib(그래프)`, `Pandas(데이터 헨들링), NGINX(SSL 인증서 활용, 보안 강화)`

### 실행 환경

* **OS:** Windows Server
* **DB:** MSSQL
* **Python 버전:** 3.10.x
* **패키지 목록:** `requirements.txt` 참고


## 2. 시스템 구조

### 대시보드 생성 구조

**시작 (main.py 실행)**

* 명령어: `python main.py`
* **main.py**가 실행되면 `main_ui.py`가 호출됩니다.

**main\_ui.py 실행**

* `main_ui.py`에서 **권한 관리**가 수행됩니다.
* **세션**에 저장된 `authenticated` 값 확인.

**권한 관리 (authenticated 확인)**

* 만약 `authenticated == False`, `login_ui.py`로 이동.
* `authenticated == True`라면 대시보드 표출 (권한이 있는 경우).

**역할 관리**

* admin일 경우 관리자 페이지 조회 가능
* user일 경우 대시보드 페이지만 조회 가능

**대시보드 페이지**

1. RO1 매크로 현황
2. 유저 세부 사항
3. 대시보드 요약
4. 멀티 클라이언트-같은 행위
5. 멀티 클라이언트-다른 행위
6. 코사인 유사도
7. 자기 유사도

## 3. 실행

### 대시보드 실행 방법

1. cmd 접속
2. 명령어 입력(python 가상환경 실행) \.venv\\Script\\activate
3. 명령어 입력(대시보드 실행) python \project\\main.py

### SSL 인증서 활용을 위한 NGINX 실행

1. cmd 접속
2. 디렉토리 이동 cd C:\\nginx
3. nginx 실행 명령어 nginx.exe 입력


## 4. 데이터베이스 스키마

### 주요 테이블

#### 대시보드 유저 관리 테이블

* user

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | id | int | NULL | 테이블 자체 생성 고유 순번 id |
    | username | nvarchar | 50 | 관리자 페이지에서 생성하는 유저 고유 id로 로그인에 사용 |
    | password\_hash | nvarchar | 255 | 관리자 페이지에서 생성하는 유저 고유 패스워드로 해쉬 상태 |
    | last\_password\_change | datetime | NULL | 최근 비밀번호 변경 일자, 180일 주기로 변경 필요 적용 |
    | role | nvarchar | 20 | 유저의 권한으로 admin, user 등의 권한 부여 |
    | created\_at | datetime | NULL | 관리자 페이지에서 유저 생성 일자 |
    | email | varchar | 255 | 유저 고유 이메일로 사내 메일 적용 |
    | blocked\_time | datetime | NULL | 로그인 10회 실패시 30분간 로그인 제어를 위한 시간 기록 |
* login\_logs

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | username | nvarchar | 255 | 유저 고유 ID |
    | login\_time | datetime | NULL | 로그인 시도 일자 |
    | status | nvarchar | 50 | 성공 실패 여부를 표기 (success, failure) |
    | ip\_address | nvarchar | 50 | 접속 시도 IP |
    | user\_agent | nvarchar | 255 | 접속 시도 Agent |
* password\_reset\_codes

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | username | varchar | 255 | 유저 고유 ID |
    | reset\_code | varchar | 255 | 메신저로 발송되는 비밀번호 변경 목적의 6자리 인증 코드 |
    | create\_time | datetime | NULL | reset\_code 생성 시간 |
    | reset\_expiry | datetime | NULL | reset\_code 만료 시간 (create\_time + 10 분) |
    | email | varchar | 50 | 메신저 발송을 위해 사용된 이메일 정보 |

#### 데이터마이닝 관련 테이블

* macro\_user\_summary

    | AID | int | NULL | RO1 계정 고유 ID |
    | --- | --- | ---- | ------------ |
    | Date | date | NULL | 분석 일자 |
    | distinction | nvarchar | 20 | 유저 구분(일반, 매크로 탐지, 매크로 의심, 블록) |
    | reason | nvarchar | 255 | 매크로 의심 이유(1개의 AID가 여러 개의 reason을 가질 경우 중복 AID 가능) |
* ro1\_block\_user

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | Date | date | NULL | 분석 일자 |
    | AID | numeric | NULL | RO1 계정 고유 ID |
    | GAME\_BLOCK\_END | datetime | NULL | 블록 만료 일자 |
* macro\_user\_cosine\_similarity

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | Date | datetime | NULL | 분석 일자 |
    | All\_user | int | NULL | 전체 유저 수(일간 100회 이상 활동 유저) |
    | All\_group | int | NULL | 유저간 유사도 기반 생성 클러스터링 결과 그룹 수 |
    | Multi\_user\_group | int | NULL | 그룹 내 유저 2명 이상의 그룹 수 |
    | Multi\_user\_group\_all\_user | int | NULL | Multi\_user\_group에 속한 유저 수 |
* macro\_user\_cosine\_similarity\_detail

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | Date | datetime | NULL | 분석 일자 |
    | srcAccountID | varchar | 10 | RO1 계정 고유 ID |
    | Group\_name | varchar | 50 | macro\_user\_groups에 정의된 그룹 번호 |
    | Total\_logtime\_Count | int | NULL | Itemlog 테이블의 logtime 기준 유니크 액션 수 |
    | Duplication\_count | int | NULL | 같은 그룹 내 유저와 같은 시간에 액션을 취한 횟수 |
    | Ratio | float | NULL | Duplication\_count / Total\_logtime\_Count |
    | IPs | nvarchar | 500 | srcAccountID가 접속한 IP 리스트 |
* cosine\_similarity\_histogram

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | Date | datetime | NULL | 분석 일자 |
    | Range\_Start | float | NULL | 구간 시작 수치 |
    | Range\_End | float | NULL | 구간 마지막 수치 |
    | Count | int | NULL | 구간 내 유저 수 |
* macro\_user\_self\_similarity

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | Date | datetime | NULL | 분석 일자 |
    | ip | varchar | 15 | 접속 IP |
    | logtime | datetime | NULL | 액션 수행 일자 |
    | Action | int | NULL | 액션 수행 코드 |
    | srcAccountID | int | NULL | RO1 계정 고유 ID |
* macro\_user\_same\_time\_diff\_action\_detail

    | COLUMN NAME | COLUMN TYPE | MAX LENGTH | SUMMARY |
    | ----------- | ----------- | ---------- | ------- |
    | srcAccountID | int | NULL | RO1 계정 고유 ID |
    | Date | datetime | NULL | 분석 일자 |
    | cosine\_similarity | real | NULL | 개인 액션의 일간 코사인 유사도 수치 |
    | self\_similarity | real | NULL | 코사인 유사도 수치를 이용한 자기 유사도 수치 |
    | logtime\_count | int | NULL | Itemlog 테이블의 logtime 기준 유니크 액션 수 |

## 5. 폴더 구조

```
project                         # 프로젝트 루트 디렉토리
│   .env                        # 가상 환경 설정 파일
│   .gitignore                   # Git에서 제외할 파일 목록
│   run.bat                      # 실행용 배치 파일
│   tree.txt                     # 폴더 구조 저장 파일
│
├── dashboard                    # 대시보드 관련 코드
│   │   main.py                  # 대시보드 실행 진입점
│   │   __init__.py              # 패키지 초기화 파일
│   │
│   ├── asset                    # 리소스 폴더 (아이콘, 이미지 등)
│   │   └── icon
│   │       └── gravity.ico      # 대시보드 아이콘
│   │
│   ├── components               # UI 구성 요소 모듈
│   │   │   comp_common.py       # 공통 컴포넌트
│   │   │   __init__.py          # 패키지 초기화 파일
│   │   │
│   │   ├── admin
│   │   │   │   comp_admin.py    # 관리자 페이지 관련 컴포넌트
│   │   │   │   __init__.py
│   │   │
│   │   ├── login                # 로그인 관련 컴포넌트
│   │   │   │   comp_ch_pwd.py   # 비밀번호 변경 컴포넌트
│   │   │   │   comp_find_pwd.py # 비밀번호 찾기 컴포넌트
│   │   │   │   comp_login.py    # 로그인 폼
│   │   │   │   __init__.py
│   │   │
│   │   ├── ro1                  # 게임 'RO1' 관련 대시보드 컴포넌트
│   │   │   │   __init__.py
│   │   │   │
│   │   │   ├── illegal_workshop
│   │   │   │   └── __init__.py  # 불법 작업장 탐지 관련 모듈
│   │   │   │
│   │   │   ├── macro            # 매크로 탐지 대시보드 모듈
│   │   │   │   │   comp_ro1_dashboard.py             # 메인 대시보드
│   │   │   │   │   comp_ro1_dashboard_cosine_sim.py  # 코사인 유사도 분석
│   │   │   │   │   comp_ro1_dashboard_cs.py          # 매크로 현황 표시 모듈
│   │   │   │   │   comp_ro1_dashboard_self_sim.py    # 자기 유사도 분석
│   │   │   │   │   comp_ro1_dashboard_stda.py        # STDA(같은 시간 다른 행동) 분석 모듈
│   │   │   │   │   comp_ro1_dashboard_stsa.py        # STSA(같은 시간 같은 행동) 분석 모듈
│   │   │   │   │   comp_ro1_dashboard_summary.py     # 대시보드 설명 및 요약
│   │   │   │   │   comp_ro1_dashboard_user_search.py # 매크로 탐지 유저 검색 기능
│   │   │   │   │   __init__.py
│   │   │
│   │   ├── sales
│   │   │   └── __init__.py        # 게임 내 매출 관련 대시보드
│   │
│   ├── functions                  # 기능별 비즈니스 로직
│   │   │   config_reader.py       # 설정 파일 읽기 모듈
│   │   │   db_connector.py        # 데이터베이스 연결 모듈
│   │   │   __init__.py
│   │   │
│   │   ├── login
│   │   │   │   change_pwd_function.py  # 비밀번호 변경 로직
│   │   │   │   find_pwd_function.py    # 비밀번호 찾기 로직
│   │   │   │   login_function.py       # 로그인 처리 로직
│   │   │   │   __init__.py
│   │   │
│   ├── ui                         # 페이지별 UI 코드
│   │   │   page_admin.py          # 관리자 페이지
│   │   │   page_dashboard.py      # 대시보드 페이지
│   │   │   page_login.py          # 로그인 페이지
│   │   │   page_main.py           # 메인 페이지
│   │   │   __init__.py
│   │
│   ├── utils                      # 유틸리티 모듈
│   │   │   exception_handler.py   # 예외 처리 모듈
│   │   │   ui_config.py           # UI 설정 모듈
│   │   │   __init__.py
│
├── datamining                     # 데이터 마이닝 관련 모듈
│   │   __init__.py
│   │
│   ├── common                     # 공통 데이터 분석 모듈
│   │   │   __init__.py
│   │   │
│   │   ├── config                 # 데이터베이스 및 API 설정
│   │   │   │   api_config.py      # API 설정 파일
│   │   │   │   db_config.py       # DB 연결 설정
│   │   │   │   __init__.py
│   │
│   ├── ro1                        # 'RO1' 게임 데이터 마이닝 모듈
│   │   │   __init__.py
│   │   │
│   │   ├── macro                  # 매크로 탐지 분석 모듈
│   │   │   │   __init__.py
│   │   │   │
│   │   │   ├── logs               # 로그 저장 폴더
│   │   │   ├── queries            # SQL 쿼리 저장 폴더
│   │   │   │   │   get_daily_user_activity_action_all.sql   # 전체(action all) 유저 활동 조회
│   │   │   │   │   get_daily_user_activity_action_one.sql   # 특정(action=1) 유저 활동 조회
│   │   │   │   │   get_data_by_date.sql                     # 특정 날짜의 데이터 조회
│   │   │   │   │   get_multi_char_user.sql                  # 다중 캐릭터 사용 유저 조회
│   │   │   │   │   get_multi_char_user_ip.sql               # 같은 IP에서 다수 캐릭터 접속 조회
│   │   │   │   │   __init__.py
│   │   │   │
│   │   │   ├── result                 # 분석 결과 저장 폴더
│   │   │   ├── src                    # 분석 코드
│   │   │   │   │   data_analysis_executor.py      # 데이터 분석 실행기
│   │   │   │   │   data_cosine_similarity.py      # 코사인 유사도 분석
│   │   │   │   │   data_logger.py                 # 데이터 로깅 모듈
│   │   │   │   │   data_same_time_diff_action.py  # 동시간대 다른 행동 분석
│   │   │   │   │   data_self_similarity.py        # 자기 유사도 분석
│   │   │   │   │   db_functions.py                # DB 함수 모음
│   │   │   │   │   __init__.py
│
└── docs                           # 문서화 폴더
    │   Table_Schema.xlsx          # 테이블 스키마 문서
```

## 6. 기능 설명

### 데이터마이닝

#### 멀티클라이언트 - 다른 행위

#### 유저간 행동 패턴 분석 (코사인 유사도)

#### 유저별 액션 코드 패턴 분석 (자기 유사도)

### 시각화

**NGINX**와 **Streamlit**을 이용하여 **HTTPS 연결**을 설정하고, **SSL 인증서**를 적용하여 보안을 강화하는 방법과, **Streamlit 대시보드**에서 **권한 관리 시스템**을 구축한 과정을 설명합니다. 이 시스템은 회사의 데이터 분석 대시보드와 그에 관련된 웹 애플리케이션의 보안 및 관리 기능을 제공합니다.

#### 주요 아키텍처

* **NGINX**: 리버스 프록시 서버 역할을 수행하여 **Streamlit 애플리케이션**으로의 트래픽을 전달하고, SSL 인증서를 사용하여 **HTTPS** 연결을 제공합니다.
* **Streamlit**: Python으로 작성된 데이터 시각화 대시보드 및 인터랙티브 웹 애플리케이션을 제공합니다. Streamlit 대시보드에는 권한 관리 기능이 포함되어 있어 사용자별 접근 제한을 수행합니다.
* **SSL 인증서**: **Gravity 인증서**를 사용하여 HTTPS 연결을 보장합니다.
* **권한 관리**: 사용자가 인증을 통해 시스템에 접근하고, 페이지별로 권한을 제한할 수 있도록 합니다.

<br>
#### NGINX

<br>
NGINX는 리버스 프록시 서버로 사용되며, 클라이언트의 요청을 Streamlit 애플리케이션으로 전달합니다. HTTPS 연결을 위해 SSL 인증서와 함께 설정을 구성합니다.
**1\. SSL 인증서 및 키 파일 준비**

* 회사에서 제공한 SSL 인증서(`.crt`)와 개인 키 파일(`.key`)을 NGINX 서버에 복사합니다

**2\. NGINX 설정 파일 \(`nginx.conf`)**

```
server {
    listen 443 ssl;
    server_name dataanalysis.gravity.co.kr;
    location / {
         proxy_pass http://localhost:8501;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto https;
         proxy_set_header Host $host;
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "upgrade";
         proxy_buffering off;
         proxy_read_timeout 86400;

    }
    ssl_certificate C:/nginx/ssl/cert.pem;
    ssl_certificate_key C:/nginx/ssl/key.pem;
}
```

**3\. SSL 인증서 적용**

* SSL 인증서와 개인 키 파일을 `nginx.conf` 파일의 경로에 설정합니다.
* `listen 443 ssl`을 통해 HTTPS를 활성화합니다.
* `proxy_pass` 설정을 통해 NGINX가 **Streamlit 애플리케이션**으로 요청을 전달하도록 구성합니다

<br>
##### STREAMLIT

<br>
Streamlit 애플리케이션에서 기본적으로 제공되는 웹 서버는 HTTP로 동작하므로, NGINX가 HTTPS를 처리하고 이를 Streamlit에 전달할 수 있도록 설정합니다.

**1\. Streamlit 대시보드 실행**
Streamlit은 `localhost:8501`에서 실행됩니다. 이를 NGINX가 **HTTPS**로 리버스 프록시할 수 있도록 설정합니다.

```
python main.py
```

#### 주요 기능:

1. **간단한 웹 애플리케이션 구축**:
    * Python 코드만으로 웹 애플리케이션을 빠르게 만들 수 있습니다.
    * 웹 페이지의 레이아웃, 텍스트, 이미지 등을 Python 코드로 간단하게 정의할 수 있습니다.
2. **Python 코드와의 통합**:
    * Streamlit은 **Python 코드와 매우 잘 통합**되어 있어, **Pandas**, **NumPy**, **Matplotlib**, **Plotly**, **Altair** 등 다른 Python 라이브러리와 함께 사용됩니다.
    * 데이터 처리, 분석, 시각화, 모델링 등의 모든 작업을 Python 코드로 처리할 수 있습니다.

<br>
#### 권한 관리

<br>
Streamlit 대시보드에서는 사용자가 로그인하여 접근할 수 있는 권한 관리 시스템을 구축합니다. 이를 위해 사용자 인증 정보를 데이터베이스에서 확인하고, 로그인 상태에 따라 페이지 별로 권한을 제한합니다.

1.사용자 로그인 및 인증
users 테이블을 사용하여 사용자 정보를 관리합니다.
로그인 시 사용자 정보를 확인하고, 세션을 생성하여 접근을 제어합니다.

2.권한 관리
사용자가 로그인한 후, 해당 사용자가 접근할 수 있는 페이지나 데이터를 제한합니다.
예를 들어, 관리자는 계정 관리 페이지에 접근 할 수 있으며, 일반 사용자는 제한된 데이터만 열람할 수 있습니다.

로그인 예시

```python (간단한 로그인 코드, 추가적인 내용은 제외)
# DB 연결
def get_db_connection():
    server, port, database, username, password = pdu_db_environment_variables()
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"
    )
    return conn

# 사용자 인증
def authenticate_user(username, password):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    return user is not None

# 로그인 페이지
def login():
    st.title('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    if st.button('Login'):
        if authenticate_user(username, password):
            st.success('Login successful!')
            # 로그인 성공 후, 대시보드 페이지로 이동
        else:
            st.error('Invalid username or password')
```

<br>
##### 비밀 번호 관리

python 라이브러리 bcrypt를 사용하여 보안 규정에 알맞은 SHA-2 수준의 암호화 적용

```python (암호화 적용 예시)
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()
```

암호 규칙 적용

```python
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

    return "valid"
```

## 7. 에러 처리

## 8. 유지 보수
