-- Schema: fiscal
-- Brief: Fiscal database definition
-- Created by: jfressineau
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: $" AS Revision;

CREATE TABLE SapiensData (
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Type VARCHAR NOT NULL,
    CreatedDate VARCHAR NOT NULL,
    SentDate VARCHAR DEFAULT NULL,
    Data BLOB NOT NULL,
    Uploaded INTEGER DEFAULT 0,
    filialSapiens VARCHAR NOT NULL,
    BusinessDate VARCHAR NOT NULL
);

CREATE UNIQUE INDEX 'sap_type_date' ON 'SapiensData' ('Type', 'BusinessDate');
CREATE INDEX 'sap_type_upload' ON 'SapiensData' ('Type', 'Uploaded');
