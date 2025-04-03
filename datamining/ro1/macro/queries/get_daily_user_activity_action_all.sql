-- ============================================================
-- 일별 사용자 활동량을 가져오는 쿼리
-- 테이블 : [dbo].[ItemLog_Baphomet]
-- 조건: 100회 이상 활동한 사용자, 모든 액션
-- 날짜 범위: date부터 다음날까지
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
ORDER BY 
    t.srcAccountID, t.logtime;