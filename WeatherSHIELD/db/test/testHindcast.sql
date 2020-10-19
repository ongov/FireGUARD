use HINDCAST
go

DECLARE @Year as INT
DECLARE @Latitude as FLOAT
DECLARE @Longitude as FLOAT

SET @Year = 1960
SET @Latitude = 46.48330
SET @Longitude = -84.51670


SELECT * FROM [HINDCAST].[FCT_Closest](@Latitude, @Longitude, @Year)

SELECT * FROM [HINDCAST].[FCT_All_Closest](@Latitude, @Longitude, @Year)

SELECT [Year], [AVG_VALUE], [GRADE]
    FROM [HINDCAST].[FCT_HistoricMatch](6, 0)
    WHERE [GRADE] > 0
    AND [YEAR] IN (SELECT [YEAR]
					FROM [HINDCAST].[DAT_Model]
					WHERE Model='Reanalysis1v04')


SELECT * FROM [HINDCAST].[FCT_Hindcast](@Latitude, @Longitude, 50)
WHERE Model='Reanalysis1v04'