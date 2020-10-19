USE [master]
GO
CREATE DATABASE [WX]
GO
ALTER DATABASE [WX] SET COMPATIBILITY_LEVEL = 100
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [WX].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [WX] SET ANSI_NULL_DEFAULT OFF
GO
ALTER DATABASE [WX] SET ANSI_NULLS OFF
GO
ALTER DATABASE [WX] SET ANSI_PADDING OFF
GO
ALTER DATABASE [WX] SET ANSI_WARNINGS OFF
GO
ALTER DATABASE [WX] SET ARITHABORT OFF
GO
ALTER DATABASE [WX] SET AUTO_CLOSE ON
GO
ALTER DATABASE [WX] SET AUTO_CREATE_STATISTICS ON
GO
ALTER DATABASE [WX] SET AUTO_SHRINK OFF
GO
ALTER DATABASE [WX] SET AUTO_UPDATE_STATISTICS ON
GO
ALTER DATABASE [WX] SET CURSOR_CLOSE_ON_COMMIT OFF
GO
ALTER DATABASE [WX] SET CURSOR_DEFAULT  GLOBAL
GO
ALTER DATABASE [WX] SET CONCAT_NULL_YIELDS_NULL OFF
GO
ALTER DATABASE [WX] SET NUMERIC_ROUNDABORT OFF
GO
ALTER DATABASE [WX] SET QUOTED_IDENTIFIER OFF
GO
ALTER DATABASE [WX] SET RECURSIVE_TRIGGERS OFF
GO
ALTER DATABASE [WX] SET  ENABLE_BROKER
GO
ALTER DATABASE [WX] SET AUTO_UPDATE_STATISTICS_ASYNC OFF
GO
ALTER DATABASE [WX] SET DATE_CORRELATION_OPTIMIZATION OFF
GO
ALTER DATABASE [WX] SET TRUSTWORTHY OFF
GO
ALTER DATABASE [WX] SET ALLOW_SNAPSHOT_ISOLATION OFF
GO
ALTER DATABASE [WX] SET PARAMETERIZATION SIMPLE
GO
ALTER DATABASE [WX] SET READ_COMMITTED_SNAPSHOT OFF
GO
ALTER DATABASE [WX] SET HONOR_BROKER_PRIORITY OFF
GO
ALTER DATABASE [WX] SET  READ_WRITE
GO
ALTER DATABASE [WX] SET RECOVERY SIMPLE
GO
ALTER DATABASE [WX] SET  MULTI_USER
GO
ALTER DATABASE [WX] SET PAGE_VERIFY CHECKSUM
GO
ALTER DATABASE [WX] SET DB_CHAINING OFF
GO

USE [WX]
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
CREATE TABLE [INPUTS].[DAT_Location](
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
CREATE TABLE [INPUTS].[DAT_Model](
    [ModelGeneratedId] [int] IDENTITY(1,1),
    [Model] varchar(20) NOT NULL,
    [Generated] [datetime] NOT NULL,
    [StartDate] [datetime] NOT NULL,
    
    CONSTRAINT PK_DatModel PRIMARY KEY([ModelGeneratedId]),
    CONSTRAINT UN_DatModel UNIQUE CLUSTERED (
        [Generated] DESC, [Model]
    )
) ON [PRIMARY]
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [INPUTS].[DAT_LocationModel](
    [LocationModelId] [int] IDENTITY(1,1),
    [ModelGeneratedId] [int] NOT NULL,
    [LocationId] [int] NOT NULL,
    
    CONSTRAINT PK_DatLocationModel PRIMARY KEY([LocationModelId]),
    CONSTRAINT UN_DatLocationModel UNIQUE CLUSTERED (
        [ModelGeneratedId], [LocationId]
    ),
    CONSTRAINT FK_DatLocationModelM FOREIGN KEY (ModelGeneratedId) REFERENCES [INPUTS].[DAT_Model]([ModelGeneratedId])
        ON DELETE CASCADE
        ON UPDATE CASCADE
    ,
    CONSTRAINT FK_DatLocationModelL FOREIGN KEY (LocationId) REFERENCES [INPUTS].[DAT_Location]([LocationId])
) ON [PRIMARY]
GO


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [INPUTS].[DAT_Forecast](
        [LocationModelId] [int] NOT NULL,
        [ForTime] [datetime] NOT NULL,
        [Member] [int] NOT NULL,
        [TMP] [float] NOT NULL,
        [RH] [float] NOT NULL,
        [WS] [float] NOT NULL,
        [WD] [float] NOT NULL,
        [APCP] [float] NOT NULL,
        
        CONSTRAINT PK_DatForecast PRIMARY KEY CLUSTERED (
            [LocationModelId], [ForTime] DESC, [Member]
        ),
        CONSTRAINT FK_DAT_Forecast FOREIGN KEY (LocationModelId) REFERENCES [INPUTS].[DAT_LocationModel]([LocationModelId])
            ON DELETE CASCADE
            ON UPDATE CASCADE
) ON [PRIMARY]
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


IF OBJECT_ID('[INPUTS].[FCT_Forecast_By_Offset]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_Forecast_By_Offset];
GO
CREATE FUNCTION [INPUTS].[FCT_Forecast_By_Offset] (
    @DateOffset AS int,
    @Latitude AS float,
    @Longitude AS float,
    @NumberDays AS int
)
RETURNS TABLE
AS
RETURN
(
    SELECT *
    FROM
    (
        SELECT
            dist.Generated,
            cur.ForTime,
            dist.Model,
            cur.Member,
            dist.Latitude,
            dist.Longitude, 
            cur.TMP,
            cur.RH,
            cur.WS,
            cur.WD,
            cur.APCP,
            dist.DISTANCE_FROM
        FROM
        (
            SELECT
                DISTINCT c.*
            FROM (SELECT [Model], MAX([Generated]) As [Generated]
                    FROM [INPUTS].[DAT_Model] m
                    WHERE [StartDate] < DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset + 1, GETDATE())), 0)
                    GROUP BY [Model]) m
            CROSS APPLY (
                SELECT TOP 1
                *
                FROM (
                    SELECT Latitude,
                            Longitude,
                            [Generated],
                            m.[Model],
                            [LocationModelId],
                            [INPUTS].DISTANCE([Latitude], [Longitude], @Latitude, @Longitude) AS DISTANCE_FROM
                    FROM
                    (SELECT [ModelGeneratedId]
                    FROM [INPUTS].[DAT_Model]
                    WHERE [Model]=m.[Model] AND [Generated]=m.[Generated]) m2
                    LEFT JOIN [INPUTS].[DAT_LocationModel] lm ON m2.[ModelGeneratedId]=lm.[ModelGeneratedId]
                    LEFT JOIN [INPUTS].[DAT_Location] loc ON loc.[LocationId]=lm.[LocationId]
                    WHERE
                        -- We should always be in a reasonable boundary if we're looking +/- 1 degree around it
                        Latitude >= (ROUND(@Latitude,0,1) - 1) AND Longitude >= (ROUND(@Longitude,0,1) - 1)
                        AND Latitude <= (ROUND(@Latitude,0,1) + 1) AND Longitude <= (ROUND(@Longitude,0,1) + 1)
                        AND NOT EXISTS (SELECT * FROM [WXSHIELD].[INPUTS].[DAT_Exclude_Points]
                                    WHERE [Latitude]=loc.[Latitude] AND [Longitude]=loc.[Longitude])
                ) s
                ORDER BY DISTANCE_FROM ASC
            ) c
        ) dist
        LEFT JOIN (SELECT *
                    FROM [INPUTS].[DAT_Forecast]
                    WHERE
                        ForTime <= DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset, GETDATE())), @NumberDays)
                        AND ForTime >= DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset, GETDATE())), 0)) cur ON
                    dist.[LocationModelId]=cur.[LocationModelId]
        ) n
        WHERE [ForTime] IS NOT NULL
    )
GO

IF OBJECT_ID('[INPUTS].[FCT_Forecast]', 'IF') IS NOT NULL
    DROP FUNCTION [INPUTS].[FCT_Forecast];
GO
CREATE FUNCTION [INPUTS].[FCT_Forecast] (
    @Latitude AS float,
    @Longitude AS float,
    @NumberDays AS int
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM [INPUTS].[FCT_Forecast_By_Offset](0, @Latitude, @Longitude, @NumberDays)
)
GO
