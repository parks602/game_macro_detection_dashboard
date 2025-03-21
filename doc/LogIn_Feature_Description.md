# 로그인 기능 설명

이 시스템은 사용자 인증 및 비밀번호 관리, 계정 등록, 인증 코드 전송, 비밀번호 변경 기능을 제공합니다. 아래에서 각 기능에 대해 설명합니다.

## 1. 사용자 등록 (`register_user`)

`register_user` 함수는 새로운 사용자 계정을 등록합니다.

### 입력 값
- `username`: 사용자의 고유 아이디
- `password`: 사용자의 비밀번호
- `email`: 사용자의 이메일
- `role`: 사용자의 역할 (예: "user", "admin")

### 기능
1. 사용자 ID 및 이메일 중복 확인
2. 비밀번호 해싱
3. 사용자 정보 DB에 저장
4. 비밀번호 재설정 코드 정보 저장

### 반환 값
- 성공: `"사용자 등록 완료"`
- 실패: `"이미 등록된 ID입니다."` 또는 `"이미 등록된 이메일입니다."`

---

## 2. 사용자 인증 (`authenticate_user`)

`authenticate_user` 함수는 사용자가 입력한 비밀번호가 올바른지 확인하고 로그인 상태를 인증합니다.

### 입력 값
- `username`: 사용자 아이디
- `password`: 사용자가 입력한 비밀번호

### 기능
1. 아이디로 사용자 정보 검색
2. 비밀번호 해싱된 값과 비교
3. 비밀번호 변경 여부 확인 (180일 이상 경과 시 비밀번호 변경 요청)

### 반환 값
- 성공: `"로그인 성공"`
- 실패: `"존재하지 않는 계정입니다."`, `"비밀번호가 틀립니다."`, `"비밀번호를 변경한 지 180일이 지났습니다. 비밀번호 변경이 필요합니다."`

---

## 3. 비밀번호 검증 (`validate_password`)

`validate_password` 함수는 비밀번호가 지정된 규칙을 만족하는지 확인합니다.

### 입력 값
- `password`: 사용자가 입력한 비밀번호

### 기능
- 최소 8자 이상
- 대문자, 소문자, 숫자, 특수문자 각 1개 이상 포함

### 반환 값
- 비밀번호가 유효하면 `"valid"`, 그렇지 않으면 해당 오류 메시지를 반환

---

## 4. 비밀번호 변경 (`change_password`)

`change_password` 함수는 사용자가 기존 비밀번호를 변경하는 기능을 제공합니다.

### 입력 값
- `username`: 사용자 아이디
- `old_password`: 기존 비밀번호
- `new_password`: 새 비밀번호
- `new_password_retype`: 새 비밀번호 확인 입력

### 기능
1. 기존 비밀번호 검증
2. 새 비밀번호와 재입력 비밀번호가 일치하는지 확인
3. 비밀번호 검증 및 해싱 후 변경

### 반환 값
- 성공: `"비밀번호가 성공적으로 변경되었습니다."`
- 실패: `"새로운 비밀번호는 기존 비밀번호와 다르게 설정해주세요."`, `"새 비밀번호와 재입력 비밀번호가 일치하지 않습니다."`

---

## 5. 비밀번호 재설정 코드 전송 (`send_reset_code`)

`send_reset_code` 함수는 사용자의 이메일로 인증 코드를 전송합니다.

### 입력 값
- `username`: 사용자 아이디 (또는 `email`)

### 기능
1. 사용자 이메일로 인증 코드 전송
2. 인증 코드 DB에 저장

### 반환 값
- 성공: `"인증 코드가 메신저로 전송되었습니다."`
- 실패: `"사용자 이메일이 존재하지 않습니다."`

---

## 6. 인증 코드 확인 (`verify_reset_code`)

`verify_reset_code` 함수는 사용자가 입력한 인증 코드가 유효한지 확인합니다.

### 입력 값
- `username`: 사용자 아이디 (또는 `email`)
- `reset_code`: 사용자가 입력한 인증 코드

### 기능
1. DB에서 인증 코드와 만료 시간을 조회
2. 인증 코드가 유효한지 확인

### 반환 값
- 성공: `True`
- 실패: `False`

---

## 7. 로그인 시도 로그 기록 (`log_login_attempt`)

`log_login_attempt` 함수는 사용자의 로그인 시도에 대한 정보를 DB에 기록합니다.

### 입력 값
- `username`: 사용자 아이디
- `status`: 로그인 상태 (성공 또는 실패)
- `ip_address`: 사용자의 IP 주소
- `user_agent`: 사용자의 사용자 에이전트

### 기능
- 로그인 시도 정보를 `login_logs` 테이블에 기록

---

## 8. 사용자 IP 주소 확인 (`get_client_ip`)

`get_client_ip` 함수는 사용자의 IP 주소를 확인합니다.

### 반환 값
- 사용자의 IP 주소

---

## 9. 사용자 에이전트 확인 (`get_user_agent`)

`get_user_agent` 함수는 사용자의 사용자 에이전트를 확인합니다.

### 반환 값
- 사용자 에이전트 문자열
