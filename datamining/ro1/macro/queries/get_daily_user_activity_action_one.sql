-- ============================================================
-- 일별 사용자 활동량을 가져오는 쿼리
-- 테이블 : [dbo].[ItemLog_Baphomet]
-- 조건: 100회 이상 활동한 사용자 (Action = 1)
-- 날짜 범위: {date}부터 {date+1}일까지
-- ============================================================

-- ============================================================
-- Action = 1 조건이 포함된 쿼리 (유저 활동이 Action=1일 때)
-- ============================================================
WITH LogtimeCounts AS (
    SELECT 
        srcAccountID,
        COUNT(DISTINCT logtime) AS logtime_count
    FROM 
        [dbo].[ItemLog_Baphomet]
    WHERE 
        logtime >= '{date}'  -- 시작일 포함
        AND logtime < DATEADD(DAY, 1, '{date}')  -- 하루 추가하여 종료 범위 설정
        AND action = 1  -- action이 1인 경우
    GROUP BY 
        srcAccountID
    HAVING 
        COUNT(DISTINCT logtime) >= 100  -- 100회 이상 활동한 사용자만
)
SELECT 
    t.srcAccountID,
    t.logtime,
    t.action,
    t.IP,
    t.SID
FROM 
    [dbo].[ItemLog_Baphomet] t
JOIN 
    LogtimeCounts lc
ON 
    t.srcAccountID = lc.srcAccountID
WHERE 
    t.logtime >= '{date}'  -- 시작일 포함
    AND t.logtime < DATEADD(DAY, 1, '{date}')  -- 하루 추가하여 종료 범위 설정
    AND t.action = 1  -- action이 1인 경우
ORDER BY 
    t.srcAccountID, t.logtime;