-- 테이블 생성
CREATE TABLE macro_user_self_similarity (
    srcAccountID INT NOT NULL,  -- 유저 식별자
    Date DATETIME NOT NULL,  -- 분석 날짜
    cosine_similarity FLOAT(4) NOT NULL,  -- 평균 코사인 유사도 (소수점 4자리)
    self_similarity FLOAT(4) NOT NULL,  -- 자기 유사도 (소수점 4자리)
    logtime_count INT NOT NULL,  -- logtime 단위 갯수
);

-- 테이블 설명 추가
EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'유저의 행동 데이터를 분석하여 코사인 유사도와 자기 유사도, logtime 단위 갯수를 저장하는 테이블입니다.',
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_self_similarity;

-- 컬럼 설명 추가
EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'유저 식별자 (srcAccountID)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_self_similarity, 
    @level2type = N'COLUMN', @level2name = srcAccountID;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'분석 날짜 (Date)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_self_similarity, 
    @level2type = N'COLUMN', @level2name = Date;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'평균 코사인 유사도 (소수점 4자리)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_self_similarity, 
    @level2type = N'COLUMN', @level2name = cosine_similarity;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'자기 유사도 (소수점 4자리)', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_self_similarity, 
    @level2type = N'COLUMN', @level2name = self_similarity;

EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'logtime 단위 갯수', 
    @level0type = N'SCHEMA', @level0name = dbo, @level1type = N'TABLE', @level1name = macro_user_self_similarity, 
    @level2type = N'COLUMN', @level2name = logtime_count;
