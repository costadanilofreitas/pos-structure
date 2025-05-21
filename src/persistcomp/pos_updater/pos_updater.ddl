-- Schema: pos_updater
-- Brief: PosUpdater component controller
-- Created by: ldlima
-- Table schema_version: must be defined for database update through the PosUpdaterPersistence component

CREATE TABLE schema_version AS
SELECT "$Author: ldlima $" AS Author,
       "$Date: 2020-06-16 16:00:00 -0300$" AS LastModifiedAt,
       "$Revision: 3c600a12c07e707e8118602ec3dc1225d21f1af6$" AS Revision;

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CREATE TABLE UpdateType (
  Id INTEGER NOT NULL PRIMARY KEY,
  Type VARCHAR NOT NULL
);

CREATE UNIQUE INDEX 'idx_UpdateType_Id' ON 'UpdateType' ('Id', 'Type');

-- ----------------------------------------------------------------
-- Currently supported update types
-- ----------------------------------------------------------------
INSERT INTO UpdateType (Id, Type) VALUES (1, 'CATALOG');
INSERT INTO UpdateType (Id, Type) VALUES (2, 'MEDIA');
INSERT INTO UpdateType (Id, Type) VALUES (3, 'USERS');
INSERT INTO UpdateType (Id, Type) VALUES (4, 'LOADERS');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CREATE TABLE UpdateStatus (
  Id INTEGER NOT NULL PRIMARY KEY,
  Status VARCHAR NOT NULL
);

CREATE UNIQUE INDEX 'idx_UpdateStatus_Id' ON 'UpdateStatus' ('Id', 'Status');

-- ----------------------------------------------------------------
-- Available update status
-- ----------------------------------------------------------------
INSERT INTO UpdateStatus (Id, Status) VALUES (1, 'PENDING');
INSERT INTO UpdateStatus (Id, Status) VALUES (2, 'APPLIED');
INSERT INTO UpdateStatus (Id, Status) VALUES (3, 'ERROR');
INSERT INTO UpdateStatus (Id, Status) VALUES (4, 'SKIPPED');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CREATE TABLE UpdatesController (
  Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  UpdateId INTEGER NOT NULL,
  UpdateName VARCHAR NOT NULL,
  TypeId INTEGER NOT NULL CONSTRAINT FK_UpdatesController_TypeId REFERENCES UpdateType(Id),
  StatusId INTEGER NOT NULL CONSTRAINT FK_UpdatesController_StatusId REFERENCES UpdateStatus(Id),
  ObtainedDate DATE NOT NULL,
  DownloadedDate DATE NULL,
  BackupDate DATE NULL,
  AppliedDate DATE NULL,
  NotifiedDate DATE NULL
);

CREATE UNIQUE INDEX 'idx_UpdatesController_UpdateId' ON 'UpdatesController' ('UpdateId', 'UpdateName');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
