-- Schema: fiscal
-- Brief: Fiscal database definition
-- Created by: ldlima
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: 635245c4a7dd3bb2b184ab05efa9ca1e6c545889$" AS Revision;

CREATE TABLE StoreStatusHistory (
    Id INTEGER NOT NULL,
    Status VARCHAR NOT NULL,
    SentToServer INTEGER NOT NULL,
    Operator INTEGER DEFAULT NULL,
    PRIMARY KEY(Id)
);

CREATE INDEX 'store_status_history_SentToServer' ON 'StoreStatusHistory' ('SentToServer');

CREATE TABLE ChatMessages (
    Id INTEGER NOT NULL,
	Origin INTEGER NOT NULL,
    CreatedTime VARCHAR NOT NULL,
	ReceivedTime VARCHAR,
    Text INTEGER NOT NULL,
	LastTimeSentToServer VARCHAR,
	ServerId VARCHAR,
    PRIMARY KEY(Id)
);

CREATE INDEX 'chat_messages_Origin_SyncedWithServer' ON 'ChatMessages' ('Origin', 'ReceivedTime');
CREATE INDEX 'chat_messages_LastTimeSentToServer' ON 'ChatMessages' ('LastTimeSentToServer');
CREATE INDEX 'chat_messages_ServerId' ON 'ChatMessages' ('ServerId');

CREATE TABLE CanceledOrders (
  OrderId INTEGER PRIMARY KEY,
  RemoteOrderId VARCHAR NOT NULL,
  Reason VARCHAR DEFAULT '',
  SentToSAC BOOLEAN DEFAULT 0
);

CREATE TABLE ProducedOrders (
  OrderId INTEGER PRIMARY KEY,
  RemoteOrderId VARCHAR NOT NULL,
  FiscalXml VARCHAR DEFAULT '',
  SentToSAC BOOLEAN DEFAULT 0
)