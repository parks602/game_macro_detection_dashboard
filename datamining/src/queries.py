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
SELECT DISTINCT srcAccountID AS AID FROM [dbo].[macro_user_cosine_similarity_detail] WHERE DATE = '{date}' AND Ratio > 0.20 AND Total_Logtime_Count > 1000
"""
GET_SELF_SIMILARITY_USER = """
SELECT DISTINCT srcAccountID AS AID FROM [dbo].[macro_user_self_similarity] WHERE DATE = '{date}' AND self_similarity > 0.97
"""
GET_ALL_ACTIVE_USER = """
SELECT
	DISTINCT t.srcAccountID AS AID
FROM
	[dbo].[ItemLog_Baphomet] t
WHERE
	t.action = 1
	AND t.logtime >= '{date}'
	AND t.logtime <  DATEADD(DAY, 1, CONVERT(DATE, '{date}'))
	AND EXISTS (
		SELECT 1
		FROM [dbo].[ItemLog_Baphomet] sub
		WHERE sub.srcAccountID = t.srcAccountID
		AND sub.action = 1
		AND sub.logtime >= '{date}'
		AND sub.logtime <  DATEADD(DAY, 1, CONVERT(DATE, '{date}'))
		GROUP BY sub.srcAccountID
		HAVING COUNT(DISTINCT sub.logtime) >=100
	)
"""


GET_BLOKED_USER = """
SELECT AID FROM [dbo].[ro1_block_user] WHERE Date = '{date}'
"""


GET_ALL_ACTIVE_USER2 = """
SELECT
	DISTINCT t.srcAccountID AS AID
FROM
	[dbo].[itemLog] t
WHERE
	t.action = 1
	AND t.logtime >= '{date}'
	AND t.logtime <  DATEADD(DAY, 1, CONVERT(DATE, '{date}'))
	AND EXISTS (
		SELECT 1
		FROM [dbo].[itemlog] sub
		WHERE sub.srcAccountID = t.srcAccountID
		AND sub.action = 1
		AND sub.logtime >= '{date}'
		AND sub.logtime <  DATEADD(DAY, 1, CONVERT(DATE, '{date}'))
		GROUP BY sub.srcAccountID
		HAVING COUNT(DISTINCT sub.logtime) >=100
	)
"""

