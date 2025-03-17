# GET_DAILY_USER_ACTIVITY = 일별 사용자 활동량을 가져오는 쿼리(조건 : 100회 이상 활동(Action=1)한 사용자)
GET_DAILY_USER_ACTIVITY = """
        WITH LogtimeCounts AS (
            SELECT 
                srcAccountID,
                COUNT(DISTINCT logtime) AS logtime_count
            FROM 
                [dbo].[ItemLog_Baphomet]
            WHERE 
                action = 1
                and logtime > '{date}'
                and logtime <= '{date} 23:59:59'
            GROUP BY 
                srcAccountID
            HAVING 
                COUNT(DISTINCT logtime) >= 100
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
            t.action = 1
            and logtime > '{date}'
            and logtime <= '{date} 23:59:59'
        GROUP BY 
            t.srcAccountID, t.logtime, t.action, t.IP, t.SID
        ORDER BY 
            t.srcAccountID, t.logtime;"""

# GET_DAILY_USER_ACTIVITY_ALL_ACTION = 일별 사용자 활동량을 가져오는 쿼리(조건 : 100회 이상 활동(ALL_ACTION)한 사용자)
GET_DAILY_USER_ACTIVITY_ALL_ACTION = """
        WITH LogtimeCounts AS (
            SELECT 
                srcAccountID,
                COUNT(DISTINCT logtime) AS logtime_count
            FROM 
                [dbo].[ItemLog_Baphomet]
            WHERE 
                logtime > '{date}'
                and logtime <= '{date} 23:59:59'
            GROUP BY 
                srcAccountID
            HAVING 
                COUNT(DISTINCT logtime) >= 100
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
            logtime > '{date}'
            and logtime <= '{date} 23:59:59'
        GROUP BY 
            t.srcAccountID, t.logtime, t.action, t.IP, t.SID
        ORDER BY 
            t.srcAccountID, t.logtime;"""

GET_UI_DATA_GROUP_USER = """
SELECT * FROM [dbo].[macro_user_groups] WHERE DATE = '{date}'
"""
GET_UI_DATA_GROUP_USER_DETAIL = """
SELECT * FROM [dbo].[macro_user_groups_detail] WHERE DATE = '{date}'
"""

GET_UI_DATA_RAGNE_HISTOGRAM = """
SELECT * FROM [dbo].[range_histogram] WHERE DATE = '{date}'
"""

GET_MULTI_CHAR_USER_IP = """
WITH SplitValues AS (
SELECT TRIM(value) AS AID
FROM [Macro_doubt_multi_char]
CROSS APPLY STRING_SPLIT(CoAID_List, ',')
WHERE Date = '{date}'
)
SELECT DISTINCT AID
FROM SplitValues
"""
GET_MULTI_CHAR_USER = """
  SELECT DISTINCT AID
  FROM [DataMining].[dbo].[Macro_multi_evidence_vol2]
where Date = '{date}' and Total_action_count > 500 and Overlap_percentage>50
"""
GET_MULTI_CHAR_USER_DATA = """
  SELECT *
  FROM [DataMining].[dbo].[Macro_multi_evidence_vol2]
where Date = '{date}'
"""

GET_MULTI_CHAR_USER_DIFF_ACTION_USER = """
SELECT DISTINCT srcAccountID as AID FROM [dbo].[macro_user_same_time_diff_action_detail] WHERE DATE = '{date}'
"""
GET_COSINE_SIMILARITY_USER = """
SELECT DISTINCT srcAccountID AS AID FROM [dbo].[macro_user_groups_detail] WHERE DATE = '{date}' AND Ratio > 0.5 AND Total_Logtime_Count > 500
"""
GET_SELF_SIMILARITY_USER = """
SELECT DISTINCT srcAccountID AS AID FROM [dbo].[macro_user_self_similarity] WHERE DATE = '{date}' AND self_similarity > 0.98  AND self_similarity < 1
"""

GET_ALL_ACTIVE_USER = """
        WITH LogtimeCounts AS (
            SELECT 
                srcAccountID,
                COUNT(DISTINCT logtime) AS logtime_count
            FROM 
                [dbo].[ItemLog_Baphomet]
            WHERE 
                logtime > '{date}'
                and logtime <= '{date} 23:59:59'
            GROUP BY 
                srcAccountID
            HAVING 
                COUNT(DISTINCT logtime) >= 100
        )
        SELECT 
            DISTINCT t.srcAccountID AS AID
        FROM 
            [dbo].[ItemLog_Baphomet] t
        JOIN 
            LogtimeCounts lc
        ON 
            t.srcAccountID = lc.srcAccountID
        WHERE 
            logtime > '{date}'
            and logtime <= '{date} 23:59:59'
        """
GET_ALL_ACTIVE_USER = """
SELECT
	DISTINCT t.srcAccountID AS AID
FROM
	[dbo].[ItemLog_Baphomet] t
WHERE
	t.action = 1
	AND t.logtime >  '{date}'
	AND t.logtime <=  '{date} 23:59:59'
	AND EXISTS (
		SELECT 1
		FROM [dbo].[ItemLog_Baphomet] sub
		WHERE sub.srcAccountID = t.srcAccountID
		AND sub.action = 1
		AND sub.logtime > '{date}'
		AND sub.logtime <=  '{date} 23:59:59'
		GROUP BY sub.srcAccountID
		HAVING COUNT(DISTINCT sub.logtime) >=100
	)
"""
GET_DAILY_SUMMARY_DATA = """
    SELECT * FROM [dbo].[macro_user_summary] WHERE Date <= '{date}' and Date > DATEADD(DAY, -10, '{date}')"""

GET_USER_SEARCH_DATA = """
SELECT m1.*
FROM [dbo].[macro_user_summary] m1
INNER JOIN(
    SELECT AID, Date
    FROM [dbo].[macro_user_summary]
    WHERE distinction = 'detection' and Date <= '{date}' and Date > DATEADD(DAY, -10, '{date}')
    ) m2
ON m1.AID = m2.AID AND m1.Date = m2.Date
WHERE m1.Date <= '{date}' and m1.Date > DATEADD(DAY, -10, '{date}')
"""

GET_UI_DATA_SELF_SIM_USER = """
SELECT * FROM [dbo].[macro_user_self_similarity] WHERE Date = '{date}'"""

GET_UI_DATA_DIFF_ACTION = """
SELECT * FROM [dbo].[macro_user_same_time_diff_action_detail] WHERE Date = '{date}'"""

GET_BLOKED_USER = """
SELECT AID FROM [dbo].[ro1_block_user] WHERE Date = '{date}' """
