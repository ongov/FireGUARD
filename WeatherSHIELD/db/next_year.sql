USE HINDCAST
GO

IF OBJECT_ID('[HINDCAST].[FCT_Hindcast_Slice]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Hindcast_Slice];
GO
CREATE FUNCTION [HINDCAST].[FCT_Hindcast_Slice] (
    @Latitude AS float,
    @Longitude AS float,
    @StartDay AS int,
    @EndDay AS int,
    @YearOffset AS int
)
RETURNS TABLE
AS
RETURN
(
SELECT
    -- HACK: use max generated time from DAT_Historic since it should be the year we matched on
    (SELECT MAX([Generated])
        FROM [HINDCAST].[DAT_Historic]) AS [Generated],
    DATEADD(YY, @YearOffset, [FAKE_DATE]) AS [ForTime],
    [Model],
    (YEAR([ForTime]) - @YearOffset) as [Member],
    [Latitude],
    [Longitude],
    [TMP],
    [RH],
    [WS],
    [WD],
    -- HACK: change to use 0800 - 1300 precip portion for day 1
    (SELECT CAST (
                CASE
                    WHEN 0 = DATEDIFF(dd, [FAKE_DATE], GETDATE())
                        THEN ([APCP] - [APCP_0800])
                    ELSE [APCP]
                END AS float)) as [APCP],
    [DISTANCE_FROM]
FROM [HINDCAST].[HINDCAST].[FCT_ALL_Closest](@Latitude, @Longitude) c
-- stick with 15 days because we know that's what it should be and we want to see any gaps
--WHERE [FAKE_DATE] > DATEADD(dd, @StartDay, DATEDIFF(dd, 0, GETDATE()))
--AND [FAKE_DATE] <= DATEADD(DD, DATEDIFF(DD, 0, GETDATE()), @NumberDays)
WHERE [FAKE_DATE] > DATEADD(dd, DATEDIFF(dd, 0, GETDATE()), @StartDay)
AND [FAKE_DATE] <= DATEADD(DD, DATEDIFF(DD, 0, GETDATE()), @EndDay)
)
GO




IF OBJECT_ID('[HINDCAST].[FCT_Hindcast]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Hindcast];
GO
CREATE FUNCTION [HINDCAST].[FCT_Hindcast] (
    @Latitude AS float,
    @Longitude AS float,
    @NumberDays AS int
)
RETURNS @T TABLE (
    --~ [DUNY] [int],
    --~ [LAST_DATE] [datetime],
    --~ [DSYS] [int],
    --~ [FIRST_DATE] [datetime],
    --~ [NYEO] [int],
    --~ [END_NEXT_DATE] [datetime],
    [Generated] [datetime],
    [ForTime] [datetime],
    [Model] varchar(20),
    [Member] [int],
    [Latitude] [float],
    [Longitude] [float],
    [TMP] [float],
    [RH] [float],
    [WS] [float],
    [WD] [float],
    [APCP] [float],
    [DISTANCE_FROM] [float]
)
AS
BEGIN
    DECLARE @DaysUntilNextYear AS int
    DECLARE @DaysSinceYearStart AS int
    DECLARE @NextYearEndOffset AS int
    DECLARE @FirstEnd AS int
    SET @DaysUntilNextYear = DATEDIFF(DD,GETDATE(),DATEADD(YY,DATEDIFF(YY,-1,GETDATE()),0)) - 1
    SET @DaysSinceYearStart = DATEDIFF(DD,GETDATE(),DATEADD(YY,DATEDIFF(YY,0,GETDATE()),0))
    SET @NextYearEndOffset = (@NumberDays - @DaysUntilNextYear) + @DaysSinceYearStart
    IF @NumberDays <= @DaysUntilNextYear
        SET @FirstEnd = @NumberDays
    ELSE
        SET @FirstEnd = @DaysUntilNextYear

    INSERT @T
    SELECT *
    FROM [HINDCAST].[FCT_Hindcast_Slice](@Latitude, @Longitude, 0, @NumberDays, 0)
    IF @NumberDays > @DaysUntilNextYear BEGIN
        INSERT @T
        SELECT *
        FROM [HINDCAST].[FCT_Hindcast_Slice](
            @Latitude,
            @Longitude,
            @DaysSinceYearStart,
            @NextYearEndOffset + 1,
            1
        )
        WHERE [Member] IN (SELECT [YEAR] FROM [HINDCAST].[HINDCAST].[DAT_Model])
    END
    RETURN
END
GO

--SELECT *
--FROM [HINDCAST].[FCT_All_Closest](46.5, -85)
--WHERE [FAKE_DATE] > DATEADD(dd, DATEDIFF(dd, 0, GETDATE()), -210)
--AND [FAKE_DATE] <= DATEADD(DD, DATEDIFF(DD, 0, GETDATE()), -200)
--ORDER BY LocationModelId, ForTime

--SELECT * FROM [HINDCAST].[FCT_Hindcast_Slice](46.5, -85, -250, -215, 1)

SELECT *
FROM [HINDCAST].[FCT_Hindcast](46.5, -85, 600)
ORDER BY [Member], [ForTime]
