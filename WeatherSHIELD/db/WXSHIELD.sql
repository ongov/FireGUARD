USE [master]
GO
CREATE DATABASE [WXSHIELD]
GO
ALTER DATABASE [WXSHIELD] SET COMPATIBILITY_LEVEL = 100
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [WXSHIELD].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [WXSHIELD] SET ANSI_NULL_DEFAULT OFF
GO
ALTER DATABASE [WXSHIELD] SET ANSI_NULLS OFF
GO
ALTER DATABASE [WXSHIELD] SET ANSI_PADDING OFF
GO
ALTER DATABASE [WXSHIELD] SET ANSI_WARNINGS OFF
GO
ALTER DATABASE [WXSHIELD] SET ARITHABORT OFF
GO
ALTER DATABASE [WXSHIELD] SET AUTO_CLOSE ON
GO
ALTER DATABASE [WXSHIELD] SET AUTO_CREATE_STATISTICS ON
GO
ALTER DATABASE [WXSHIELD] SET AUTO_SHRINK OFF
GO
ALTER DATABASE [WXSHIELD] SET AUTO_UPDATE_STATISTICS ON
GO
ALTER DATABASE [WXSHIELD] SET CURSOR_CLOSE_ON_COMMIT OFF
GO
ALTER DATABASE [WXSHIELD] SET CURSOR_DEFAULT  GLOBAL
GO
ALTER DATABASE [WXSHIELD] SET CONCAT_NULL_YIELDS_NULL OFF
GO
ALTER DATABASE [WXSHIELD] SET NUMERIC_ROUNDABORT OFF
GO
ALTER DATABASE [WXSHIELD] SET QUOTED_IDENTIFIER OFF
GO
ALTER DATABASE [WXSHIELD] SET RECURSIVE_TRIGGERS OFF
GO
ALTER DATABASE [WXSHIELD] SET  ENABLE_BROKER
GO
ALTER DATABASE [WXSHIELD] SET AUTO_UPDATE_STATISTICS_ASYNC OFF
GO
ALTER DATABASE [WXSHIELD] SET DATE_CORRELATION_OPTIMIZATION OFF
GO
ALTER DATABASE [WXSHIELD] SET TRUSTWORTHY OFF
GO
ALTER DATABASE [WXSHIELD] SET ALLOW_SNAPSHOT_ISOLATION OFF
GO
ALTER DATABASE [WXSHIELD] SET PARAMETERIZATION SIMPLE
GO
ALTER DATABASE [WXSHIELD] SET READ_COMMITTED_SNAPSHOT OFF
GO
ALTER DATABASE [WXSHIELD] SET HONOR_BROKER_PRIORITY OFF
GO
ALTER DATABASE [WXSHIELD] SET  READ_WRITE
GO
ALTER DATABASE [WXSHIELD] SET RECOVERY SIMPLE
GO
ALTER DATABASE [WXSHIELD] SET  MULTI_USER
GO
ALTER DATABASE [WXSHIELD] SET PAGE_VERIFY CHECKSUM
GO
ALTER DATABASE [WXSHIELD] SET DB_CHAINING OFF
GO

USE [WXSHIELD]
GO
CREATE SCHEMA [LOG] AUTHORIZATION db_owner
GO
CREATE USER [wx_readwrite] FOR LOGIN [wx_readwrite] WITH DEFAULT_SCHEMA=[LOG]
CREATE USER [wx_readonly] FOR LOGIN [wx_readonly] WITH DEFAULT_SCHEMA=[LOG]
GO

GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::LOG TO wx_readwrite
GRANT SELECT, INSERT, DELETE, UPDATE, EXECUTE ON SCHEMA::LOG TO wx_readonly
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [LOG].[FCT_Forecast](
    [IP] [varchar](15) NOT NULL,
    [Timeof] datetime NOT NULL,
    [Latitude] [float] NOT NULL,
    [Longitude] [float] NOT NULL,
    [Offset] [int] NOT NULL,
    [NumDays] [int] NOT NULL,
    [Query] [varchar](max) NOT NULL,
    
) ON [PRIMARY]
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