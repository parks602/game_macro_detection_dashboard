-- 테이블 생성
CREATE TABLE macro_user_same_time_diff_action_detail (
    Date DATETIME NOT NULL,  -- 분석일시
    ip VARCHAR(15) NOT NULL,  -- IP 주소
    logtime DATETIME NOT NULL,  -- 게임 로그 시간
    Action INT NOT NULL,  -- 유저 액션 (예: 0=이동, 1=공격 등)
    srcAccountID INT NOT NULL,  -- 유저 식별자
);

-- 테이블 설명 추가
EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'유저의 액션 데이터와 로그 시간을 기록한 테이블로, 분석일시와 로그시간을 기준으로 유저 행동을 분석합니다.',
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_same_time_diff_action_detail;

-- 컬럼 설명 추가
EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'분석일시 (Date)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_same_time_diff_action_detail, 
    @level2type = N'COLUMN', @level2name = Date;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'IP 주소 (ip)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_same_time_diff_action_detail, 
    @level2type = N'COLUMN', @level2name = ip;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'게임 로그 시간 (logtime)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_same_time_diff_action_detail, 
    @level2type = N'COLUMN', @level2name = logtime;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'유저 액션 코드 (Action)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_same_time_diff_action_detail, 
    @level2type = N'COLUMN', @level2name = Action;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'유저 식별자 (srcAccountID)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_same_time_diff_action_detail, 
    @level2type = N'COLUMN', @level2name = srcAccountID;
