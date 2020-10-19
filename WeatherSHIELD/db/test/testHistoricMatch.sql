use hindcast
go

UPDATE 
[HINDCAST].[DAT_Historic]
SET [Generated]='2016-03-01 12:34:56'
WHERE HistoricGeneratedId=38

UPDATE 
[HINDCAST].[DAT_Historic]
SET [Generated]='2016-04-01 12:34:56'
WHERE HistoricGeneratedId=39

IF OBJECT_ID('[HINDCAST].[VIEW_HistoricMatch]', 'view') IS NOT NULL
    DROP VIEW [HINDCAST].[VIEW_HistoricMatch];
GO
CREATE VIEW [HINDCAST].[VIEW_HistoricMatch]
AS
SELECT
    h.[Generated],
    m.[Year],
    m.[Month],
    m.[Value],
    DATEADD(YYYY, [Year]-1900, DATEADD(MM, [Month]-1, 0)) AS FAKE_DATE
FROM 
    [HINDCAST].[DAT_HistoricMatch] m
    LEFT JOIN [HINDCAST].[DAT_Historic] h ON m.HistoricGeneratedId=h.HistoricGeneratedId
WHERE m.HistoricGeneratedId =26

GO

SELECT *
FROM [HINDCAST].[HINDCAST].[DAT_Historic]


select *
from [HINDCAST].[FCT_HistoricMatch]()
ORDER BY [GRADE] DESC