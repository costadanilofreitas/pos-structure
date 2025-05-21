-- noinspection SqlNoDataSourceInspectionForFile

-- Schema: product
-- Brief: Control item availability
-- Created by: ealmeida
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author: Emilson $" AS Author,
       "$Date: 2016-01-24 13:00:00 -0300 (Sun, 24 Jan 2016) $" AS LastModifiedAt,
       "$Revision: f3eae67843c4150bef18ff2a0b2818021de42659$" AS Revision;

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
