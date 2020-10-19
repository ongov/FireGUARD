USE WXSHIELD
GO

CREATE SCHEMA [INPUTS] AUTHORIZATION db_owner
GO

GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::INPUTS TO wx_readwrite
GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::INPUTS TO wx_readonly
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [INPUTS].[DAT_Exclude_Points](
    [Latitude] [float] NOT NULL,
    [Longitude] [float] NOT NULL,
    CONSTRAINT PK_DatLocationModel PRIMARY KEY([Latitude], [Longitude]),
) ON [PRIMARY]
GO

-- add in all the points that are in lakes
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (42, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (42, -83)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (42, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (42, -81)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (43, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (44, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (44, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (44, -77)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (45, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (45, -86)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (45, -83)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (45, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (45, -81)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (45, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (46, -85)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (46, -83)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (46, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (47, -91)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (47, -90)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (47, -89)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (47, -88)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (47, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (47, -86)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (47, -85)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (48, -89)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (48, -88)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (48, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (48, -86)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (49, -95)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (52, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (52, -79)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (53, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (53, -79)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (54, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (54, -81)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (54, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (54, -79)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (55, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (55, -81)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (55, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (55, -79)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (55, -73)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -86)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -85)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -84)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -83)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -81)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -78)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -77)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56, -74)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -89)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -88)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -86)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -85)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -84)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -83)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -81)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -79)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -78)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (57, -77)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -92)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -91)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -90)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -89)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -88)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -87)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -86)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -85)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -84)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -83)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -82)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -81)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -80)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -79)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (58, -78)
GO

-- insert reanalysis lake points
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (42.856399536132812, -86.25)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (44.761100769042969, -86.25)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (44.761100769042969, -82.5)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (44.761100769042969, -80.625)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (46.665798187255859, -86.25)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (48.570499420166016, -88.125)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (52.379901885986328, -80.625)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (52.379901885986328, -78.75)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (54.284599304199219, -80.625)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56.189300537109375, -86.25)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56.189300537109375, -84.375)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56.189300537109375, -82.5)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56.189300537109375, -80.625)
INSERT INTO [INPUTS].[DAT_Exclude_Points]([Latitude], [Longitude]) VALUES (56.189300537109375, -76.875)
GO

USE HINDCAST
GO

IF OBJECT_ID('[HINDCAST].[FCT_Closest]', 'IF') IS NOT NULL
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

-- now for 2016
USE WX_201601
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

USE WX_201602
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

USE WX_201603
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

USE WX_201604
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

USE WX_201605
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

USE WX_201606
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

USE WX_201607
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

USE WX_201608
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

USE WX_201609
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

USE WX_201610
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

USE WX_201611
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

USE WX_201612
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


-- now for 2017
USE WX_201701
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

USE WX_201702
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

USE WX_201703
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

USE WX_201704
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

USE WX_201705
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

USE WX_201706
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

USE WX_201707
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

USE WX_201708
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

USE WX_201709
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

USE WX_201710
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

USE WX_201711
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

USE WX_201712
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

--~ -- now for 2016
--~ USE WX_201601
--~ GO

--~ USE WX_201602
--~ GO

--~ USE WX_201603
--~ GO

--~ USE WX_201604
--~ GO

--~ USE WX_201605
--~ GO

--~ USE WX_201606
--~ GO

--~ USE WX_201607
--~ GO

--~ USE WX_201608
--~ GO

--~ USE WX_201609
--~ GO

--~ USE WX_201610
--~ GO

--~ USE WX_201611
--~ GO

--~ USE WX_201612
--~ GO


--~ -- now for 2017
--~ USE WX_201701
--~ GO

--~ USE WX_201702
--~ GO

--~ USE WX_201703
--~ GO

--~ USE WX_201704
--~ GO

--~ USE WX_201705
--~ GO

--~ USE WX_201706
--~ GO

--~ USE WX_201707
--~ GO

--~ USE WX_201708
--~ GO

--~ USE WX_201709
--~ GO

--~ USE WX_201710
--~ GO

--~ USE WX_201711
--~ GO

--~ USE WX_201712
--~ GO
