CREATE TABLE INPUTS__DAT_Location(
    LocationId int IDENTITY(1,1),
    Latitude float NOT NULL,
    Longitude float NOT NULL,
    CONSTRAINT PK_DatLocation PRIMARY KEY(LocationId)
);

CREATE TABLE INPUTS__DAT_Location(
    LocationId int NOT NULL,
    Latitude float NOT NULL,
    Longitude float NOT NULL
);

ALTER TABLE INPUTS__DAT_Location ADD (
    CONSTRAINT PK_DatLocation PRIMARY KEY(LocationId));

CREATE SEQUENCE SQ_DAT_Location START WITH 1;

CREATE OR REPLACE TRIGGER TG_DatLocation
BEFORE INSERT ON INPUTS__DAT_Location
FOR EACH ROW
BEGIN
  SELECT SQ_DAT_Location.NEXTVAL
  INTO   :new.LocationId
  FROM   dual;
END;


CREATE TABLE INPUTS__DAT_Model(
    ModelGeneratedId int IDENTITY(1,1),
    Model varchar(20) NOT NULL,
    Generated timestamp NOT NULL,
    StartDate timestamp NOT NULL,
    
    CONSTRAINT PK_DatModel PRIMARY KEY(ModelGeneratedId),
    CONSTRAINT UN_DatModel UNIQUE CLUSTERED (
        Generated DESC, Model
    )
);

CREATE TABLE INPUTS__DAT_LocationModel(
    [LocationModelId] int IDENTITY(1,1),
    [ModelGeneratedId] int NOT NULL,
    [LocationId] int NOT NULL,
    
    CONSTRAINT PK_DatLocationModel PRIMARY KEY([LocationModelId]),
    CONSTRAINT UN_DatLocationModel UNIQUE CLUSTERED (
        [ModelGeneratedId], [LocationId]
    ),
    CONSTRAINT FK_DatLocationModelM FOREIGN KEY (ModelGeneratedId) REFERENCES INPUTS__DAT_Model([ModelGeneratedId])
        ON DELETE CASCADE
        ON UPDATE CASCADE
    ,
    CONSTRAINT FK_DatLocationModelL FOREIGN KEY (LocationId) REFERENCES INPUTS__DAT_Location([LocationId])
);

CREATE TABLE INPUTS__DAT_Forecast(
        [LocationModelId] int NOT NULL,
        [ForTime] timestamp NOT NULL,
        [Member] int NOT NULL,
        [TMP] float NOT NULL,
        [RH] float NOT NULL,
        [WS] float NOT NULL,
        [WD] float NOT NULL,
        [APCP] float NOT NULL,
        
        CONSTRAINT PK_DatForecast PRIMARY KEY CLUSTERED (
            [LocationModelId], [ForTime] DESC, [Member]
        ),
        CONSTRAINT FK_DAT_Forecast FOREIGN KEY (LocationModelId) REFERENCES INPUTS__DAT_LocationModel([LocationModelId])
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

IF OBJECT_ID('INPUTS__DISTANCE', 'FN') IS NOT NULL DROP FUNCTION INPUTS__DISTANCE;

CREATE FUNCTION INPUTS__DISTANCE
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


IF OBJECT_ID('INPUTS__FCT_Forecast_By_Offset', 'IF') IS NOT NULL
    DROP FUNCTION INPUTS__FCT_Forecast_By_Offset;
GO
CREATE FUNCTION INPUTS__FCT_Forecast_By_Offset (
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
                    FROM INPUTS__DAT_Model m
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
                    FROM INPUTS__DAT_Model
                    WHERE [Model]=m.[Model] AND [Generated]=m.[Generated]) m2
                    LEFT JOIN INPUTS__DAT_LocationModel lm ON m2.[ModelGeneratedId]=lm.[ModelGeneratedId]
                    LEFT JOIN INPUTS__DAT_Location loc ON loc.[LocationId]=lm.[LocationId]
                    WHERE
                        -- We should always be in a reasonable boundary if we're looking +/- 1 degree around it
                        Latitude >= (ROUND(@Latitude,0,1) - 1) AND Longitude >= (ROUND(@Longitude,0,1) - 1)
                        AND Latitude <= (ROUND(@Latitude,0,1) + 1) AND Longitude <= (ROUND(@Longitude,0,1) + 1)
                        AND NOT EXISTS (SELECT * FROM WXSHIELD__INPUTS.[DAT_Exclude_Points]
                                    WHERE [Latitude]=loc.[Latitude] AND [Longitude]=loc.[Longitude])
                ) s
                ORDER BY DISTANCE_FROM ASC
            ) c
        ) dist
        LEFT JOIN (SELECT *
                    FROM INPUTS__DAT_Forecast
                    WHERE
                        ForTime <= DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset, GETDATE())), @NumberDays)
                        AND ForTime >= DATEADD(DD, DATEDIFF(DD, 0, DATEADD(DD, @DateOffset, GETDATE())), 0)) cur ON
                    dist.[LocationModelId]=cur.[LocationModelId]
        ) n
        WHERE [ForTime] IS NOT NULL
    )
GO

IF OBJECT_ID('INPUTS__FCT_Forecast', 'IF') IS NOT NULL
    DROP FUNCTION INPUTS__FCT_Forecast;
GO
CREATE FUNCTION INPUTS__FCT_Forecast (
    @Latitude AS float,
    @Longitude AS float,
    @NumberDays AS int
)
RETURNS TABLE
AS
RETURN
(
    SELECT * FROM INPUTS__FCT_Forecast_By_Offset(0, @Latitude, @Longitude, @NumberDays)
)
GO
