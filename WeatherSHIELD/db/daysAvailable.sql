USE [WX_201609]
GO

--SELECT [Generated],[ForTime],[Member],[Latitude],[Longitude],[TMP],[RH],[WS],[WD],[APCP],[Model]
SELECT CONVERT(date, [Generated]) AS [ForDate], COUNT(DISTINCT [ForTime]) AS [DaysAvailable]
FROM [INPUTS].[DAT_Forecast] f
LEFT JOIN [INPUTS].[DAT_LocationModel] lm ON f.LocationModelId=lm.LocationModelId
LEFT JOIN [INPUTS].[DAT_Model] m ON m.ModelGeneratedId = lm.ModelGeneratedId
LEFT JOIN [INPUTS].[DAT_Location] l ON l.LocationId = lm.LocationId
WHERE [Model]='AFFES'
--AND MONTH([Generated])=6
--AND DAY([Generated])=4
GROUP BY CONVERT(date, [Generated])
ORDER BY CONVERT(date, [Generated])
D