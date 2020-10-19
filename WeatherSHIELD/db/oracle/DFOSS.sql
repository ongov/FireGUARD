USE [master]
GO
CREATE DATABASE [DFOSS]
GO
ALTER DATABASE [DFOSS] SET COMPATIBILITY_LEVEL = 100
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [DFOSS].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [DFOSS] SET ANSI_NULL_DEFAULT OFF
GO
ALTER DATABASE [DFOSS] SET ANSI_NULLS OFF
GO
ALTER DATABASE [DFOSS] SET ANSI_PADDING OFF
GO
ALTER DATABASE [DFOSS] SET ANSI_WARNINGS OFF
GO
ALTER DATABASE [DFOSS] SET ARITHABORT OFF
GO
ALTER DATABASE [DFOSS] SET AUTO_CLOSE ON
GO
ALTER DATABASE [DFOSS] SET AUTO_CREATE_STATISTICS ON
GO
ALTER DATABASE [DFOSS] SET AUTO_SHRINK OFF
GO
ALTER DATABASE [DFOSS] SET AUTO_UPDATE_STATISTICS ON
GO
ALTER DATABASE [DFOSS] SET CURSOR_CLOSE_ON_COMMIT OFF
GO
ALTER DATABASE [DFOSS] SET CURSOR_DEFAULT  GLOBAL
GO
ALTER DATABASE [DFOSS] SET CONCAT_NULL_YIELDS_NULL OFF
GO
ALTER DATABASE [DFOSS] SET NUMERIC_ROUNDABORT OFF
GO
ALTER DATABASE [DFOSS] SET QUOTED_IDENTIFIER OFF
GO
ALTER DATABASE [DFOSS] SET RECURSIVE_TRIGGERS OFF
GO
ALTER DATABASE [DFOSS] SET  ENABLE_BROKER
GO
ALTER DATABASE [DFOSS] SET AUTO_UPDATE_STATISTICS_ASYNC OFF
GO
ALTER DATABASE [DFOSS] SET DATE_CORRELATION_OPTIMIZATION OFF
GO
ALTER DATABASE [DFOSS] SET TRUSTWORTHY OFF
GO
ALTER DATABASE [DFOSS] SET ALLOW_SNAPSHOT_ISOLATION OFF
GO
ALTER DATABASE [DFOSS] SET PARAMETERIZATION SIMPLE
GO
ALTER DATABASE [DFOSS] SET READ_COMMITTED_SNAPSHOT OFF
GO
ALTER DATABASE [DFOSS] SET HONOR_BROKER_PRIORITY OFF
GO
ALTER DATABASE [DFOSS] SET  READ_WRITE
GO
ALTER DATABASE [DFOSS] SET RECOVERY SIMPLE
GO
ALTER DATABASE [DFOSS] SET  MULTI_USER
GO
ALTER DATABASE [DFOSS] SET PAGE_VERIFY CHECKSUM
GO
ALTER DATABASE [DFOSS] SET DB_CHAINING OFF
GO

USE [DFOSS]
GO
CREATE SCHEMA [INPUTS] AUTHORIZATION db_owner
GO
CREATE USER [wx_readwrite] FOR LOGIN [wx_readwrite] WITH DEFAULT_SCHEMA=[INPUTS]
CREATE USER [wx_readonly] FOR LOGIN [wx_readonly] WITH DEFAULT_SCHEMA=[INPUTS]
GO
GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::INPUTS TO wx_readwrite
GRANT SELECT ON SCHEMA::INPUTS TO wx_readonly
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
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


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [INPUTS].[CT_WSTN](
    [WSTNCODE] [varchar](3) NULL,
    [ORGUNIT] [varchar](3) NULL,
    [LASTACTIVEYEAR] [numeric](10) NULL,
    [WSTNTYPE] [varchar](20) NULL,
    [WSTNNAME] [varchar](100) NULL,
    [MOTHERSTNID] [varchar](3) NULL,
    [REGION] [varchar](3) NULL,
    [RESPSECTOR] [varchar](3) NULL,
    [WSECTOR] [varchar](3) NULL,
    [DATEESTABLISHED] [datetime] NULL,
    [DATEDISCONTINUED] [datetime] NULL,
    [OPERATORTYPE] [varchar](3) NULL,
    [INSTRUMENTTYPE] [varchar](30) NULL,
    [ZONE] [numeric](12,2) NULL,
    [BASEMAP] [numeric](12,2) NULL,
    [BLOCK] [numeric](12,2) NULL,
    [SUBBLOCK] [numeric](12,2) NULL,
    [SUBBLOCK2ND] [numeric](12,2) NULL,
    [LATITUDE] [numeric](12,4) NULL,
    [WINDADJFACTOR] [numeric](12,2) NULL,
    [CREATEDBY] [varchar](20) NULL,
    [CREATEDDATE] [datetime] NULL,
    [LASTUPDATEBY] [varchar](20) NULL,
    [LASTUPDATEDATE] [datetime] NULL,
    [LONGITUDE] [numeric](12,4) NULL,
    [FMA] [varchar](100) NULL,
    [BACKBONE] [numeric](10) NULL,
    [ELEVATION] [numeric](10) NULL,
    [AGENCY] [varchar](3) NULL,

) ON [PRIMARY]
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [INPUTS].[WFORECAST](
    [FORECASTID] [int] NOT NULL,
    [WSTNCODE] [varchar](3) NULL,
    [FORECASTTYPE] [char](1) NULL,
    [FORECASTDATETIME] [datetime] NULL,
    [FORECASTAREA] [varchar](3) NULL,
    [FR] [varchar](3) NULL,
    [TEMP] [numeric](3,1) NULL,
    [RH] [numeric](3) NULL,
    [WINDDIR] [numeric](3) NULL,
    [WINDSPEED] [numeric](3,1) NULL,
    [ADJWINDSPEED] [numeric](3,1) NULL,
    [RAINFALL] [numeric](10,4) NULL,
    [FFMC] [numeric](10,4) NULL,
    [DMC] [numeric](10,4) NULL,
    [DC] [numeric](10,4) NULL,
    [FWI] [numeric](10,4) NULL,
    [BUI] [numeric](10,4) NULL,
    [ISI] [numeric](10,4) NULL,
    [DSR] [numeric](10,4) NULL,
    [CREATEDBY] [varchar](20) NULL,
    [CREATEDDATE] [datetime] NULL,
    [LASTUPDATEDBY] [varchar](20) NULL,
    [LASTUPDATEDDATE] [datetime] NULL,
    [SDMC] [numeric](10,4) NULL,
    
) ON [PRIMARY]
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [INPUTS].[WOBSERV](
    [WOBSERVID] [int] NOT NULL,
    [WSTNCODE] [varchar](3) NULL,
    [OBSDATE] [datetime] NULL,
    [OBSTIME] [int] NULL,
    [OBSTYPE] [char](1) NULL,
    [TEMP] [numeric](10,4) NULL,
    [RELHUMID] [numeric](10,4) NULL,
    [WINDDIR] [numeric](10,4) NULL,
    [WINDSPEED] [numeric](10,4) NULL,
    [ADJWINDSPEED] [numeric](10,4) NULL,
    [RAINFALL] [numeric](10,4) NULL,
    [FFMC] [numeric](10,4) NULL,
    [DMC] [numeric](10,4) NULL,
    [DC] [numeric](10,4) NULL,
    [ISI] [numeric](10,4) NULL,
    [BUI] [numeric](10,4) NULL,
    [FWI] [numeric](10,4) NULL,
    [DSR] [numeric](10,4) NULL,
    [CREATEDBY] [varchar](30) NULL,
    [CREATEDDATE] [datetime] NULL,
    [LASTUPDATEDBY] [varchar](30) NULL,
    [LASTUPDATEDDATE] [datetime] NULL,
    [SDMC] [numeric](10,4) NULL,
    
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [INPUTS].[ACTIVEFIRE](
    [FIREID] [numeric](15) NOT NULL,
    [FIRENAME] [varchar](7) NOT NULL,
    [LATITUDE] [numeric](12,4) NULL,
    [LONGITUDE] [numeric](12,4) NULL,

) ON [PRIMARY]
GO


-- ***************************************************
--                    END OF TABLES
-- ***************************************************

IF OBJECT_ID('[INPUTS].[FCT_Observed_By_Date]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_Observed_By_Date];
GO
CREATE FUNCTION [INPUTS].[FCT_Observed_By_Date] (
    @ForDate AS datetime,
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    -- trying to make this the same shape as other FCT_Forecast
    SELECT
        -- HACK: just repeat this since unsure about how rest of system will respond to multiple ForTime / Generated
        DATEADD(HOUR, 18, DATEDIFF(DAY, 0, f.OBSDATE)) as [Generated],
        --~ DATEADD(HOUR, 13, DATEDIFF(DAY, 0, f.CREATEDDATE)) as [Generated],
        -- observations are always for 18z since we only get 1300 readings
        DATEADD(HOUR, 18, DATEDIFF(DAY, 0, f.OBSDATE)) as [ForTime],
        -- use WSTNCODE as Model because it's text in other FCT
        'Observed' as [Model],
        s.WSTNCODE as [Member],
        s.LATITUDE as [Latitude],
        s.LONGITUDE as [Longitude],
        f.TEMP as TMP,
        f.RELHUMID as RH,
        COALESCE(f.ADJWINDSPEED, f.WINDSPEED) as WS,
        f.WINDDIR as WD,
        f.RAINFALL as APCP,
        f.FFMC,
        f.DMC,
        f.DC,
        f.ISI,
        f.BUI,
        f.FWI,
        o.RAINFALL as APCP_0800,
        s.DISTANCE_FROM
    FROM
        (SELECT TOP (@NumberStations) *
            FROM
            (
                SELECT DATEADD(YYYY, DATEDIFF(yyyy, 0, @ForDate)-1, 0) as last_year, c.*, [INPUTS].DISTANCE([Latitude], [Longitude], @Latitude, @Longitude) AS DISTANCE_FROM
                FROM [INPUTS].[CT_WSTN] c
                -- do this so other statements always start with AND
                WHERE 0=0
                -- don't use spring stations
                AND c.WSTNCODE NOT LIKE '4%'
                -- base data has some invalid station locations
                AND c.[LONGITUDE] IS NOT NULL AND c.[LATITUDE] IS NOT NULL
                -- if discontinued then don't use it
                AND c.[DATEDISCONTINUED] IS NULL
                -- assume that we're going to start it again this year if we used it last year
                -- LASTACTIVEYEAR doesn't appear to be updated correctly on the DFOSS end
                -- so use anything that was updated since Jan 1 of last year or created this year
                AND (c.[LASTUPDATEDATE] >= DATEADD(YYYY, DATEDIFF(yyyy, 0, @ForDate)-1, 0)
                    OR c.[CREATEDDATE] >= DATEADD(YYYY, DATEDIFF(yyyy, 0, @ForDate), 0))
            ) stns
        ORDER BY DISTANCE_FROM ASC) s
        LEFT JOIN (
            SELECT *
            FROM [INPUTS].[WOBSERV]
            WHERE OBSDATE < DATEADD(dd, 0, DATEDIFF(dd, 0, @ForDate))
            AND OBSDATE >= DATEADD(dd, -1, DATEDIFF(dd, 0, @ForDate))
            AND obstime = 1300
        ) f ON s.WSTNCODE=f.WSTNCODE
        LEFT JOIN (
            SELECT *
            FROM [INPUTS].[WOBSERV]
            WHERE OBSDATE < DATEADD(dd, 1, DATEDIFF(dd, 0, @ForDate))
            AND OBSDATE >= DATEADD(dd, 0, DATEDIFF(dd, 0, @ForDate))
            AND obstime = 800
        ) o ON o.WSTNCODE=f.WSTNCODE
)
GO

IF OBJECT_ID('[INPUTS].[FCT_Observed]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_Observed];
GO
CREATE FUNCTION [INPUTS].[FCT_Observed] (
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM [INPUTS].[FCT_Observed_By_Date](GETDATE(), @Latitude, @Longitude, @NumberStations)
)
GO

IF OBJECT_ID('[INPUTS].[FCT_FWIObserved_By_Date]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_FWIObserved_By_Date];
GO
CREATE FUNCTION [INPUTS].[FCT_FWIObserved_By_Date] (
    @ForDate AS datetime,
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    -- get nearest non-null station out of the specified number of stations
    SELECT TOP 1 *
    FROM [INPUTS].[FCT_Observed_By_Date](@ForDate, @Latitude, @Longitude, @NumberStations)
    WHERE [ForTime] IS NOT NULL
    ORDER BY [ForTime], DISTANCE_FROM
)
GO

IF OBJECT_ID('[INPUTS].[FCT_FWIObserved_By_Offset]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_FWIObserved_By_Offset];
GO
CREATE FUNCTION [INPUTS].[FCT_FWIObserved_By_Offset] (
    @DateOffset AS int,
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM [INPUTS].[FCT_FWIObserved_By_Date](DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset + 1, GETDATE())), 0), @Latitude, @Longitude, @NumberStations)
)
GO

IF OBJECT_ID('[INPUTS].[FCT_FWIObserved]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_FWIObserved];
GO
CREATE FUNCTION [INPUTS].[FCT_FWIObserved] (
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM [INPUTS].[FCT_FWIObserved_By_Date](GETDATE(), @Latitude, @Longitude, @NumberStations)
)
GO

IF OBJECT_ID('[INPUTS].[FCT_Forecast_By_Date]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_Forecast_By_Date];
GO
CREATE FUNCTION [INPUTS].[FCT_Forecast_By_Date] (
    @ForDate AS datetime,
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    -- trying to make this the same shape as other FCT_Forecast
    SELECT
        f.CREATEDDATE as [Generated],
        --DATEADD(hh, 18 - DATEPART(HOUR, f.FORECASTDATETIME), f.FORECASTDATETIME) as [ForTime],
        --f.FORECASTDATETIME,
        -- forecasts are always for 18z
        DATEADD(HOUR, 18, DATEDIFF(DAY, 0, f.FORECASTDATETIME)) as [ForTime],
        -- use WSTNCODE as Model because it's text in other FCT
        'Forecast' as [Model],
        s.WSTNCODE as [Member],
        --~ -- do we need to keep this as a number?
        --~ 'AFFES' as [Model],
        --~ s.WSTNCODE as [Member],
        s.LATITUDE as [Latitude],
        s.LONGITUDE as [Longitude],
        f.TEMP as TMP,
        f.RH,
        COALESCE(f.ADJWINDSPEED, f.WINDSPEED) as WS,
        f.WINDDIR as WD,
        f.RAINFALL as APCP,
        f.FFMC,
        f.DMC,
        f.DC,
        f.ISI,
        f.BUI,
        f.FWI,
        s.DISTANCE_FROM
    FROM
        (SELECT TOP (@NumberStations) *
            FROM
            (
                SELECT DATEADD(YYYY, DATEDIFF(yyyy, 0, @ForDate)-1, 0) as last_year, c.*, [INPUTS].DISTANCE([Latitude], [Longitude], @Latitude, @Longitude) AS DISTANCE_FROM
                FROM [INPUTS].[CT_WSTN] c
                -- do this so other statements always start with AND
                WHERE 0=0
                -- don't use spring stations
                AND c.WSTNCODE NOT LIKE '4%'
                -- base data has some invalid station locations
                AND c.[LONGITUDE] IS NOT NULL AND c.[LATITUDE] IS NOT NULL
                -- if discontinued then don't use it
                AND c.[DATEDISCONTINUED] IS NULL
                -- assume that we're going to start it again this year if we used it last year
                -- LASTACTIVEYEAR doesn't appear to be updated correctly on the DFOSS end
                -- so use anything that was updated since Jan 1 of last year or created this year
                AND (c.[LASTUPDATEDATE] >= DATEADD(YYYY, DATEDIFF(yyyy, 0, @ForDate)-1, 0)
                    OR c.[CREATEDDATE] >= DATEADD(YYYY, DATEDIFF(yyyy, 0, @ForDate), 0))
            ) stns
        ORDER BY DISTANCE_FROM ASC) s
        LEFT JOIN (
            SELECT *
            FROM [INPUTS].[WFORECAST]
            WHERE CREATEDDATE=(SELECT MAX(CREATEDDATE) FROM [INPUTS].[WFORECAST])
        ) f ON s.WSTNCODE=f.WSTNCODE
)
GO

IF OBJECT_ID('[INPUTS].[FCT_Forecast]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_Forecast];
GO
CREATE FUNCTION [INPUTS].[FCT_Forecast] (
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM [INPUTS].[FCT_Forecast_By_Date](GETDATE(), @Latitude, @Longitude, @NumberStations)
)
GO

IF OBJECT_ID('[INPUTS].[FCT_FWIForecast]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_FWIForecast];
GO
CREATE FUNCTION [INPUTS].[FCT_FWIForecast] (
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS TABLE
AS
RETURN
(
    -- get nearest non-null station out of the specified number of stations
    SELECT TOP 1 *
    FROM [INPUTS].[FCT_Forecast](@Latitude, @Longitude, @NumberStations)
    WHERE [ForTime] IS NOT NULL
    ORDER BY DISTANCE_FROM, [ForTime]
)
GO



IF OBJECT_ID('[INPUTS].[FCT_Actuals]') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_Actuals];
GO
CREATE FUNCTION [INPUTS].[FCT_Actuals] (
    @DateOffset AS int,
    @NumberDays AS int,
    @Latitude AS float,
    @Longitude AS float,
    @NumberStations as int = 3
)
RETURNS @T TABLE (
    [Generated] [datetime],
    [ForTime] [datetime],
    [Model] varchar(20),
    [Member] varchar(3),
    [Latitude] [float],
    [Longitude] [float],
    [TMP] [float],
    [RH] [float],
    [WS] [float],
    [WD] [float],
    [APCP] [float],
    [FFMC] [float],
    [DMC] [float],
    [DC] [float],
    [ISI] [float],
    [BUI] [float],
    [FWI] [float],
    [APCP_0800] [float],
    [DISTANCE_FROM] [float]
)
AS
BEGIN
    DECLARE @FirstDay AS [datetime]
    DECLARE @LastDay AS [datetime]
    SET @FirstDay = DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset + 1, GETDATE())), 0)
    SET @LastDay = DATEADD(DD, @NumberDays, @FirstDay)
    INSERT @T
    SELECT w.*
    FROM
    (
        SELECT
            DISTINCT DATEADD(HOUR, 18, DATEDIFF(DAY, 0, f.FORECASTDATETIME)) AS [ForTime]
        FROM
            [INPUTS].[WFORECAST] f
        WHERE
            FORECASTDATETIME < @LastDay
            AND FORECASTDATETIME > @FirstDay
    ) d
    CROSS APPLY
    (
        SELECT * FROM INPUTS.FCT_FWIObserved_By_Date(d.[ForTime], @Latitude, @Longitude, @NumberStations)
    ) w
    ORDER BY [ForTime]
    RETURN
END
GO
