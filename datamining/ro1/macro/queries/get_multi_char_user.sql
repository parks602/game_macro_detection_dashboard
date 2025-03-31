SELECT DISTINCT AID
FROM [DataMining].[dbo].[Macro_multi_evidence_vol2]
WHERE Date = '{date}' 
AND Total_action_count > 500 
AND Overlap_percentage > 50;
