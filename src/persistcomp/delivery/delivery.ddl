-- noinspection SqlNoDataSourceInspectionForFile

-- Schema: delivery
-- Brief: Delivery database definition
-- Created by: ldlima
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: 090a199fb1567078ug6t8trt8duc140d7a753449$" AS Revision;

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
);

CREATE TABLE EventType (
  Id INTEGER PRIMARY KEY,
  EventName VARCHAR NOT NULL
);

CREATE UNIQUE INDEX 'idx_EventType_Id' ON 'EventType' ('Id', 'EventName');
INSERT INTO EventType (Id, EventName) VALUES (1, 'OrderReadyToDelivery');
INSERT INTO EventType (Id, EventName) VALUES (2, 'PosLogisticDispatched');
INSERT INTO EventType (Id, EventName) VALUES (3, 'PosLogisticDelivered');

CREATE TABLE DeliveryEvents (
  OrderId INTEGER NOT NULL,
  RemoteOrderId VARCHAR NOT NULL,
  EventType VARCHAR NOT NULL,
  EventData VARCHAR NOT NULL,
  InsertTime DATE NOT NULL,
  ServerAck BOOLEAN DEFAULT 0
);

CREATE UNIQUE INDEX 'idx_DeliveryEvents_Id' ON 'DeliveryEvents' ('OrderId', 'EventType');
