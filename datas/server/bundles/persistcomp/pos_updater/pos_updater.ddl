-- Schema: pos_updater
-- Brief: PosUpdater component controller
-- Created by: ldlima
-- Table schema_version: must be defined for database update through the PosUpdaterPersistence component

CREATE TABLE schema_version AS
SELECT "$Author: ldlima $" AS Author,
       "$Date: 2020-04-22 14:00:00 -0300$" AS LastModifiedAt,
       "$Revision: 1bff8e6687c9fbb94e90400f33b484a2c09641cf$" AS Revision;

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CREATE TABLE UpdateType (
  UpdateId INTEGER NOT NULL PRIMARY KEY,
  UpdateType VARCHAR NOT NULL
);

CREATE UNIQUE INDEX 'idx_UpdateType_UpdateId' ON 'UpdateType' ('UpdateId');

-- ----------------------------------------------------------------
-- Currently supported update types
-- ----------------------------------------------------------------
INSERT INTO UpdateType (UpdateId, UpdateType) VALUES (1, 'CATALOG');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CREATE TABLE UpdatesController (
  Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  VersionId VARCHAR NOT NULL,
  UpdateTypeId INTEGER NOT NULL CONSTRAINT FK_UpdatesController_UpdateTypeId REFERENCES UpdateType(UpdateId),
  ObtainedDate DATE NOT NULL,
  DownloadedDate DATE NULL,
  VerifiedDate DATE NULL,
  BackupDate DATE NULL,
  AppliedDate DATE NULL
);

CREATE UNIQUE INDEX 'idx_UpdatesController_Id' ON 'UpdatesController' ('Id');
CREATE UNIQUE INDEX 'idx_UpdatesController_VersionId' ON 'UpdatesController' ('VersionId', 'UpdateTypeId');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
