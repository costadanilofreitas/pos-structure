-- Schema: product
-- Brief: this schema represents the products catalog and all its configuration parameters
-- Created by: amerolli
-- Table schema_version: must be defined for database update through the Persistence Component
CREATE TABLE schema_version AS
SELECT "$Author: Emilson $" AS Author,
       "$Date: 2016-01-24 13:00:00 -0300 (Sun, 24 Jan 2016) $" AS LastModifiedAt,
       "$Revision: ag12g9b5b14321f39425ae2e803a0113392c37dd$" AS Revision;

-- ------------------------- --
-- ------------------------- --
-- Ruptura schema definition --
-- ------------------------- --
-- ------------------------- --

-- -----------------------------------------
-- Main database tables for ruptura catalog
-- -----------------------------------------


CREATE TABLE RupturaItens (
    ProductCode     INTEGER,
    Period          DATETIME,
    SessionId       VARCHAR,
    EnableDate      DATETIME,
    EnableSessionId VARCHAR
);

CREATE TABLE RupturaSnapshot (
    ID               INTEGER PRIMARY KEY AUTOINCREMENT,
    InactiveProdList VARCHAR NOT NULL
);

CREATE TABLE RupturaCurrentState (
    SnapshotID  INTEGER NOT NULL,
    Environment VARCHAR NOT NULL,
    Processed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(SnapshotID, Environment),
    FOREIGN KEY(SnapshotID) REFERENCES RupturaSnapshot(ID)
);

CREATE TABLE CleanRuptureEvent (
    EventDate VARCHAR,
    Processed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(EventDate)
)