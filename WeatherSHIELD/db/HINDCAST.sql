USE [master]
GO
CREATE DATABASE [HINDCAST]
GO
ALTER DATABASE [HINDCAST] SET COMPATIBILITY_LEVEL = 100
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [HINDCAST].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [HINDCAST] SET ANSI_NULL_DEFAULT OFF
GO
ALTER DATABASE [HINDCAST] SET ANSI_NULLS OFF
GO
ALTER DATABASE [HINDCAST] SET ANSI_PADDING OFF
GO
ALTER DATABASE [HINDCAST] SET ANSI_WARNINGS OFF
GO
ALTER DATABASE [HINDCAST] SET ARITHABORT OFF
GO
ALTER DATABASE [HINDCAST] SET AUTO_CLOSE ON
GO
ALTER DATABASE [HINDCAST] SET AUTO_CREATE_STATISTICS ON
GO
ALTER DATABASE [HINDCAST] SET AUTO_SHRINK OFF
GO
ALTER DATABASE [HINDCAST] SET AUTO_UPDATE_STATISTICS ON
GO
ALTER DATABASE [HINDCAST] SET CURSOR_CLOSE_ON_COMMIT OFF
GO
ALTER DATABASE [HINDCAST] SET CURSOR_DEFAULT  GLOBAL
GO
ALTER DATABASE [HINDCAST] SET CONCAT_NULL_YIELDS_NULL OFF
GO
ALTER DATABASE [HINDCAST] SET NUMERIC_ROUNDABORT OFF
GO
ALTER DATABASE [HINDCAST] SET QUOTED_IDENTIFIER OFF
GO
ALTER DATABASE [HINDCAST] SET RECURSIVE_TRIGGERS OFF
GO
ALTER DATABASE [HINDCAST] SET  ENABLE_BROKER
GO
ALTER DATABASE [HINDCAST] SET AUTO_UPDATE_STATISTICS_ASYNC OFF
GO
ALTER DATABASE [HINDCAST] SET DATE_CORRELATION_OPTIMIZATION OFF
GO
ALTER DATABASE [HINDCAST] SET TRUSTWORTHY OFF
GO
ALTER DATABASE [HINDCAST] SET ALLOW_SNAPSHOT_ISOLATION OFF
GO
ALTER DATABASE [HINDCAST] SET PARAMETERIZATION SIMPLE
GO
ALTER DATABASE [HINDCAST] SET READ_COMMITTED_SNAPSHOT OFF
GO
ALTER DATABASE [HINDCAST] SET HONOR_BROKER_PRIORITY OFF
GO
ALTER DATABASE [HINDCAST] SET  READ_WRITE
GO
ALTER DATABASE [HINDCAST] SET RECOVERY SIMPLE
GO
ALTER DATABASE [HINDCAST] SET  MULTI_USER
GO
ALTER DATABASE [HINDCAST] SET PAGE_VERIFY CHECKSUM
GO
ALTER DATABASE [HINDCAST] SET DB_CHAINING OFF
GO

USE [HINDCAST]
GO
CREATE SCHEMA [INPUTS] AUTHORIZATION db_owner
GO
CREATE USER [wx_readwrite] FOR LOGIN [wx_readwrite] WITH DEFAULT_SCHEMA=[INPUTS]
CREATE USER [wx_readonly] FOR LOGIN [wx_readonly] WITH DEFAULT_SCHEMA=[INPUTS]
GO
GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::INPUTS TO wx_readwrite
GRANT SELECT ON SCHEMA::INPUTS TO wx_readonly
GO


IF OBJECT_ID('[INPUTS].[DISTANCE]', 'FN') IS NOT NULL
    DROP FUNCTION [INPUTS].[DISTANCE];
GO
CREATE FUNCTION [INPUTS].[DISTANCE]
(
    @LatitudeA AS float,
    @LongitudeA AS float,
    @LatitudeB AS float,
    @LongitudeB AS float
)
RETURNS float
BEGIN
    DECLARE @a geography;
    DECLARE @b geography;
    SET @a = geography::Point(@LatitudeA, @LongitudeA, 4326);
    SET @b = geography::Point(@LatitudeB, @LongitudeB, 4326);
    return @a.STDistance(@b);
END
GO



IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name='HINDCAST')
BEGIN
EXEC('CREATE SCHEMA [HINDCAST] AUTHORIZATION db_owner')
END
GO

-- HINDCAST data is immutable, but need to write it the first time
GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::HINDCAST TO wx_readwrite
GRANT SELECT ON SCHEMA::HINDCAST TO wx_readonly
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [HINDCAST].[DAT_Historic](
    [HistoricGeneratedId] [int] IDENTITY(1,1),
    [Generated] [datetime] NOT NULL,
    
    CONSTRAINT PK_DatHistoric PRIMARY KEY([HistoricGeneratedId]),
    CONSTRAINT UN_DatHistoric UNIQUE CLUSTERED (
        [Generated]
    )
) ON [PRIMARY]
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [HINDCAST].[DAT_HistoricMatch](
    [HistoricGeneratedId] [int] NOT NULL,
    [Year] [int] NOT NULL,
    [Month] [int] NOT NULL,
    [Value] [float] NOT NULL
    
    CONSTRAINT PK_DatHistoricMatch PRIMARY KEY CLUSTERED (
        [HistoricGeneratedId], [Year], [Month]
    ),
    CONSTRAINT FK_DatHistoricMatch FOREIGN KEY (HistoricGeneratedId) REFERENCES [HINDCAST].[DAT_Historic]([HistoricGeneratedId])
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ON [PRIMARY]
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [HINDCAST].[DAT_Location](
    [LocationId] [int] IDENTITY(1,1),
    [Latitude] [float] NOT NULL,
    [Longitude] [float] NOT NULL,
    
    CONSTRAINT PK_DatLocation PRIMARY KEY([LocationId]),
    CONSTRAINT UN_DatLocation UNIQUE CLUSTERED (
        [Latitude], [Longitude]
    )
) ON [PRIMARY]
GO



SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [HINDCAST].[DAT_Model](
    [ModelGeneratedId] [int] IDENTITY(1,1),
    [Model] varchar(20) NOT NULL,
    -- use Year instead of Generated because it actually affects performance quite a bit
    [Year] [int] NOT NULL,
    
    CONSTRAINT PK_DatModel PRIMARY KEY([ModelGeneratedId]),
    CONSTRAINT UN_DatModel UNIQUE CLUSTERED (
        [Year], [Model]
    )
) ON [PRIMARY]
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [HINDCAST].[DAT_LocationModel](
    [LocationModelId] [int] IDENTITY(1,1),
    [ModelGeneratedId] [int] NOT NULL,
    [LocationId] [int] NOT NULL,
    
    CONSTRAINT PK_DatLocationModel PRIMARY KEY([LocationModelId]),
    CONSTRAINT UN_DatLocationModel UNIQUE CLUSTERED (
        [ModelGeneratedId], [LocationId]
    ),
    CONSTRAINT FK_DatLocationModelM FOREIGN KEY (ModelGeneratedId) REFERENCES [HINDCAST].[DAT_Model]([ModelGeneratedId])
        ON DELETE CASCADE
        ON UPDATE CASCADE
    ,
    CONSTRAINT FK_DatLocationModelL FOREIGN KEY (LocationId) REFERENCES [HINDCAST].[DAT_Location]([LocationId])
) ON [PRIMARY]
GO


-- was ~3300 mb originally
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [HINDCAST].[DAT_Hindcast](
    [LocationModelId] [int] NOT NULL,
    [ForTime] [datetime] NOT NULL,
    [TMP] [float] NOT NULL,
    [RH] [float] NOT NULL,
    [WS] [float] NOT NULL,
    [WD] [float] NOT NULL,
    [APCP] [float] NOT NULL,
    [APCP_0800] [float] NOT NULL
    
    CONSTRAINT PK_DatHindcast PRIMARY KEY CLUSTERED (
        [LocationModelId], [ForTime]
    ),
    CONSTRAINT FK_DatHindcast FOREIGN KEY (LocationModelId) REFERENCES [HINDCAST].[DAT_LocationModel]([LocationModelId])
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ON [PRIMARY]
GO

-- ***************************************************
--                    END OF TABLES
-- ***************************************************

IF OBJECT_ID('[HINDCAST].[VIEW_HistoricMatch]', 'view') IS NOT NULL
    DROP VIEW [HINDCAST].[VIEW_HistoricMatch];
GO
IF OBJECT_ID('[HINDCAST].[FCT_Historic_By_Date]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Historic_By_Date];
GO
CREATE FUNCTION [HINDCAST].[FCT_Historic_By_Date](
    @FirstDay AS [datetime]
)
RETURNS TABLE
AS
RETURN(
    SELECT
        h.[Generated],
        m.[Year],
        m.[Month],
        m.[Value],
        DATEADD(YYYY, [Year]-1900, DATEADD(MM, [Month]-1, 0)) AS FAKE_DATE
    FROM 
        (SELECT TOP 1 [Generated], [HistoricGeneratedId]
            FROM [HINDCAST].[DAT_Historic]
            WHERE DATEADD(DD, DATEDIFF(DD, 0, [Generated]), 0) <= @FirstDay
            ORDER BY [Generated] DESC) h
        LEFT JOIN [HINDCAST].[DAT_HistoricMatch] m ON h.[HistoricGeneratedId]=m.[HistoricGeneratedId]
)
GO


IF OBJECT_ID('[HINDCAST].[FCT_Closest]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Closest];
GO
CREATE FUNCTION [HINDCAST].[FCT_Closest] (
    @Latitude AS float,
    @Longitude AS float
)
RETURNS TABLE
AS
RETURN
(
    SELECT TOP 1
    *
    FROM (
        SELECT [LocationId], [Latitude], [Longitude], [INPUTS].[DISTANCE](LATITUDE, LONGITUDE, @Latitude, @Longitude) AS DISTANCE_FROM
        FROM [HINDCAST].[DAT_Location] loc
        WHERE
            NOT EXISTS (SELECT * FROM [WXSHIELD].[INPUTS].[DAT_Exclude_Points]
                        WHERE [Latitude]=loc.[Latitude] AND [Longitude]=loc.[Longitude])
            -- We should always be in a reasonable boundary if we're looking +/- 3 degrees around it
            -- since resolution is 2.5 degrees
            AND Latitude >= (ROUND(@Latitude,0,1) - 3) AND Longitude >= (ROUND(@Longitude,0,1) - 3)
            AND Latitude <= (ROUND(@Latitude,0,1) + 3) AND Longitude <= (ROUND(@Longitude,0,1) + 3)
    ) s
    ORDER BY DISTANCE_FROM ASC
)


GO

IF OBJECT_ID('[HINDCAST].[FCT_All_Closest]', 'IF') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_All_Closest];
GO
CREATE FUNCTION [HINDCAST].[FCT_All_Closest] (
    @FirstDay AS [datetime],
    @Latitude AS float,
    @Longitude AS float
)
RETURNS TABLE
AS
RETURN
(
    SELECT
        m.[Model],
        c.[Latitude],
        c.[Longitude],
        (SELECT MAX([Generated])
            FROM [HINDCAST].[DAT_Historic]
            WHERE DATEADD(DD, DATEDIFF(DD, 0, [Generated]), 0) <= @FirstDay) as [Generated],
        cur.*, 
        MONTH(cur.ForTime) as [Month],
        DAY(cur.ForTime) as [Day],
        DATEADD(YYYY, YEAR(@FirstDay) - YEAR(cur.ForTime), cur.ForTime) as [FAKE_DATE],
        DISTANCE_FROM
    FROM
        [HINDCAST].[FCT_Closest](@Latitude, @Longitude) c
        LEFT JOIN [HINDCAST].[DAT_LocationModel] lm ON lm.[LocationId]=c.[LocationId]
        LEFT JOIN [HINDCAST].[DAT_Model] m ON m.[ModelGeneratedId]=lm.[ModelGeneratedId]
        LEFT JOIN [HINDCAST].[HINDCAST].[DAT_Hindcast] cur ON lm.[LocationModelId]=cur.[LocationModelId]
)

GO


IF OBJECT_ID('[HINDCAST].[FCT_Quadtratic]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Quadtratic];
GO
CREATE FUNCTION [HINDCAST].[FCT_Quadtratic]
(
    @Value AS float,
    @a as float,
    @b as float,
    @c as float,
    @d as float,
    @e as float
)
RETURNS float
AS
BEGIN
    RETURN @a * POWER(@Value, 4) + @b * POWER(@Value, 3) + @c * POWER(@Value, 2) + @d * @Value + @e
END
GO

IF OBJECT_ID('[HINDCAST].[FCT_WeightMonth]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_WeightMonth];
GO
CREATE FUNCTION [HINDCAST].[FCT_WeightMonth]
(
    @Month AS int
)
RETURNS float
AS
BEGIN
    DECLARE @a as float
    DECLARE @b as float
    DECLARE @c as float
    DECLARE @d as float
    DECLARE @e as float
    SET @a = -1.7
    SET @b = 30
    SET @c = -146
    SET @d = 201
    SET @e = 140
    RETURN [HINDCAST].[FCT_Quadtratic](@Month, @a, @b, @c, @d, @e)
END
GO


IF OBJECT_ID('[HINDCAST].[FCT_WeightMatch]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_WeightMatch];
GO
CREATE FUNCTION [HINDCAST].[FCT_WeightMatch]
(
    @Value AS float
)
RETURNS float
AS
BEGIN
    DECLARE @a as float
    DECLARE @b as float
    DECLARE @c as float
    DECLARE @d as float
    DECLARE @e as float
    SET @a = 0
    SET @b = 140
    SET @c = -341
    SET @d = 277
    SET @e = -75
    RETURN [HINDCAST].[FCT_Quadtratic](@Value, @a, @b, @c, @d, @e)
END
GO



IF OBJECT_ID('[HINDCAST].[FCT_GradeHistoric]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_GradeHistoric];
GO
CREATE FUNCTION [HINDCAST].[FCT_GradeHistoric]
(
    @Value AS float,
    @Month AS int
)
RETURNS float
AS
BEGIN
    RETURN [HINDCAST].[FCT_WeightMonth](@Month) * [HINDCAST].[FCT_WeightMatch](@Value)
END
GO


IF OBJECT_ID('[HINDCAST].[FCT_HistoricMatch_By_Offset]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_HistoricMatch_By_Offset];
GO
CREATE FUNCTION [HINDCAST].[FCT_HistoricMatch_By_Offset]
(
    @DateOffset AS int
)
RETURNS @T TABLE (
            [Generated] [datetime],
            [Year] int,
            [AVG_VALUE] float,
            [GRADE] float
        )
AS
BEGIN
    DECLARE @FirstDay AS [datetime]
    DECLARE @NumberMonths AS int
    DECLARE @OffsetMonths AS int
    DECLARE @MinRatioScore AS float
    SET @FirstDay = DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset, GETDATE())), 0)
    SET @NumberMonths = 5
    SET @OffsetMonths = 0
    SET @MinRatioScore = .725
    INSERT @T
    SELECT
        h.[Generated],
        h.[Year],
        AVG(s.[Value]) AS AVG_VALUE,
        -- needs to equal 1 when score is perfect
        (SUM(MONTH_GRADE) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH))) AS GRADE
    FROM
    (
        SELECT DISTINCT [Year]
        FROM [HINDCAST].[DAT_Model]
        WHERE [YEAR] < YEAR(@FirstDay)
    ) m
    CROSS APPLY
    (
        SELECT *
        FROM [HINDCAST].[FCT_Historic_By_Date](@FirstDay)
        WHERE [Year]=m.[Year]
    ) h
    CROSS APPLY
    (
        SELECT
            DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]) AS START_FROM,
            [HINDCAST].[FCT_GradeHistoric]([Value], (DATEDIFF(MM, DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]), FAKE_DATE) + @OffsetMonths)) AS MONTH_GRADE,
            Value,
            (DATEDIFF(MM, DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]), FAKE_DATE) + @OffsetMonths) AS WHICH_MONTH,
            FAKE_DATE as FOR_MONTH
        FROM [HINDCAST].[FCT_Historic_By_Date](@FirstDay)
        WHERE
            [FAKE_DATE] >= DATEADD(MM, @OffsetMonths, h.[FAKE_DATE])
            -- not <= because that would be @NumberMonths + 1 months
            AND [FAKE_DATE] < DATEADD(MM, @NumberMonths, DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]))
    ) s
    WHERE MONTH(FAKE_DATE)=MONTH(@FirstDay)
    GROUP BY h.[Generated], h.[Year], s.START_FROM
    RETURN
END
GO


IF OBJECT_ID('[HINDCAST].[FCT_HistoricMatch]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_HistoricMatch];
GO
CREATE FUNCTION [HINDCAST].[FCT_HistoricMatch]
(
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM [HINDCAST].[FCT_HistoricMatch_By_Offset](0)
)
GO

IF OBJECT_ID('[HINDCAST].[FCT_Hindcast_Slice]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Hindcast_Slice];
GO
CREATE FUNCTION [HINDCAST].[FCT_Hindcast_Slice] (
    @FirstDay AS [datetime],
    @Latitude AS float,
    @Longitude AS float,
    @StartDay AS [datetime],
    @NumberDays AS int,
    @YearOffset AS int
)
RETURNS TABLE
AS
RETURN
(
SELECT
    c.[Generated],
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
                    WHEN 0 = DATEDIFF(dd, [FAKE_DATE], @FirstDay)
                        THEN ([APCP] - [APCP_0800])
                    ELSE [APCP]
                END AS float)) as [APCP],
    [DISTANCE_FROM]
FROM [HINDCAST].[HINDCAST].[FCT_ALL_Closest](@FirstDay, @Latitude, @Longitude) c
WHERE DATEADD(YY, @YearOffset, [FAKE_DATE]) > @StartDay
-- HACK: do this instead of EndDay because some years have Feb 29 and so have more days
AND DATEADD(YY, @YearOffset, [FAKE_DATE]) < DATEADD(DD, @NumberDays, @StartDay)
)
GO




IF OBJECT_ID('[HINDCAST].[FCT_Hindcast_By_Offset]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Hindcast_By_Offset];
GO
CREATE FUNCTION [HINDCAST].[FCT_Hindcast_By_Offset] (
    @DateOffset AS int,
    @Latitude AS float,
    @Longitude AS float,
    @NumberDays AS int
)
RETURNS @T TABLE (
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
    DECLARE @YearEnd AS [datetime]
    DECLARE @MaxDays AS int
    DECLARE @NextYearEndOffset AS int
    DECLARE @CurrentOffset AS int
    DECLARE @FirstDay AS [datetime]
    DECLARE @CurrentStart AS [datetime]
    DECLARE @CurrentEnd AS int
    DECLARE @DaysPicked AS int
    SET @FirstDay = DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset, GETDATE())), 0)
    SET @CurrentStart = @FirstDay
    SET @CurrentOffset = 0
    SET @DaysPicked = 0
    SET @YearEnd = CAST(CAST(((YEAR(@FirstDay)) + 1) AS VARCHAR(4)) + '-01-01' AS DATE)
    SET @MaxDays = DATEDIFF(DD, @CurrentStart, @YearEnd)
    -- hard code a limit here because we don't want to duplicate data output
    IF @NumberDays > 365
        SET @NumberDays = 365
    WHILE @NumberDays > @DaysPicked AND @DaysPicked < 365 BEGIN
        IF @NumberDays < @DaysPicked + @MaxDays
            SET @CurrentEnd = (@NumberDays - @DaysPicked)
        ELSE
            SET @CurrentEnd = @MaxDays
        SET @DaysPicked = @DaysPicked + @CurrentEnd
        INSERT @T
        SELECT
            *
        FROM [HINDCAST].[FCT_Hindcast_Slice](@FirstDay, @Latitude, @Longitude, @CurrentStart, @CurrentEnd, @CurrentOffset)
        WHERE [Member] IN (SELECT [YEAR] FROM [HINDCAST].[HINDCAST].[DAT_Model])
        SET @CurrentOffset = @CurrentOffset + 1
        -- NOTE: this is until Jan 1 @ 00:00:00 since we pick dates <= it and we need 18z of Dec 31
        SET @CurrentStart = CAST(CAST((YEAR(@FirstDay) + @CurrentOffset) AS VARCHAR(4)) + '-01-01' AS DATE)
        SET @MaxDays = 365
    END
    RETURN
END
GO

IF OBJECT_ID('[HINDCAST].[FCT_Hindcast]') IS NOT NULL
    DROP FUNCTION [HINDCAST].[FCT_Hindcast];
GO
CREATE FUNCTION [HINDCAST].[FCT_Hindcast] (
    @Latitude AS float,
    @Longitude AS float,
    @NumberDays AS int
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM [HINDCAST].[FCT_Hindcast_By_Offset](0, @Latitude, @Longitude, @NumberDays)
)
GO
