CREATE TABLE LOG__FCT_Forecast(
    IP varchar(15) NOT NULL,
    Timeof timestamp NOT NULL,
    Latitude float NOT NULL,
    Longitude float NOT NULL,
    Offset int NOT NULL,
    NumDays int NOT NULL,
    Query varchar(1000) NOT NULL,
    PRIMARY KEY (IP, Timeof, Latitude, Longitude, Offset, NumDays)
);

CREATE TABLE INPUTS__DAT_Exclude_Points(
    Latitude float NOT NULL,
    Longitude float NOT NULL,
    CONSTRAINT PK_DatLocationModel PRIMARY KEY(Latitude, Longitude)
);

-- add in all the points that are in lakes
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (42, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (42, -83);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (42, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (42, -81);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (43, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (44, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (44, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (44, -77);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (45, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (45, -86);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (45, -83);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (45, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (45, -81);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (45, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (46, -85);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (46, -83);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (46, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (47, -91);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (47, -90);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (47, -89);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (47, -88);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (47, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (47, -86);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (47, -85);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (48, -89);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (48, -88);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (48, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (48, -86);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (49, -95);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (52, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (52, -79);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (53, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (53, -79);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (54, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (54, -81);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (54, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (54, -79);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (55, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (55, -81);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (55, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (55, -79);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (55, -73);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -86);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -85);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -84);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -83);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -81);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -78);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -77);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56, -74);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -89);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -88);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -86);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -85);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -84);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -83);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -81);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -79);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -78);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (57, -77);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -92);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -91);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -90);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -89);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -88);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -87);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -86);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -85);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -84);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -83);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -82);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -81);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -80);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -79);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (58, -78);

-- insert reanalysis lake points;
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (42.856399536132812, -86.25);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (44.761100769042969, -86.25);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (44.761100769042969, -82.5);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (44.761100769042969, -80.625);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (46.665798187255859, -86.25);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (48.570499420166016, -88.125);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (52.379901885986328, -80.625);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (52.379901885986328, -78.75);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (54.284599304199219, -80.625);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56.189300537109375, -86.25);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56.189300537109375, -84.375);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56.189300537109375, -82.5);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56.189300537109375, -80.625);
INSERT INTO INPUTS__DAT_Exclude_Points(Latitude, Longitude) VALUES (56.189300537109375, -76.875);