WITH SplitValues AS (
    SELECT TRIM(value) AS AID
    FROM [Macro_doubt_multi_char]
    CROSS APPLY STRING_SPLIT(CoAID_List, ',')
    WHERE Date = '{date}'
)
SELECT DISTINCT AID
FROM SplitValues;
