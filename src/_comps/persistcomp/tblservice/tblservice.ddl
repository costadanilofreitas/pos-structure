-- --------------------------------------------------------------------------------
-- Copyright (C) 2018 MWneo Corporation
-- Copyright (C) 2018 Omega Tech Enterprises Ltd. 
-- (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
--
-- Schema: tblservice
-- Brief: Used by the Table Service Manager
-- Created by: amerolli
-- Table schema_version: must be defined for database update through the Persistence Component
CREATE TABLE schema_version AS
SELECT "$Author: amerolli $" AS Author, 
       "$Date: 2018-09-10 10:00:00 -0300 (Mon, 10 Set 2018) $" AS LastModifiedAt,
       "$Revision: 9959b1143febe9a857398ffe21d12feb54c489ac$" AS Revision;


--
-- Table TableType:
--   Definitions of table types.
CREATE TABLE TableType (
    TypeId            INTEGER PRIMARY KEY,
    Descr             VARCHAR(32)
    );
INSERT INTO TableType (TypeId, Descr) VALUES
    (1, "Seat"),
    (2, "Tab");


--
-- Table TableStatus:
--   Definitions of table types.
CREATE TABLE TableStatus(
    Status            INTEGER PRIMARY KEY,
    Descr             VARCHAR(32)
    ); 

INSERT INTO TableStatus (Status, Descr) VALUES
    (1, "Available"),
    (2, "Waiting2BSeated"),
    (3, "Seated"),
    (4, "InProgress"),
    (5, "Linked"),
    (6, "Totaled"),
    (7, "Closed");

      
--
-- Table RestaurantTable:
--   Holds the table information and its status.
--   <NumberOfSeats> Set here is the pre-configured size of the table.
--   <POSId>         POS identification currently servicing with the Table.
--   <LinkedTableId> If table <Status> is *Linked*, this is the referenced to the linked table.
CREATE TABLE RestaurantTable (
    TableId           VARCHAR(32) NOT NULL,
    NumberOfSeats     INTEGER NOT NULL,
    TypeId            INTEGER NOT NULL DEFAULT 1,
    Status            INTEGER NOT NULL DEFAULT 1,
    POSId             INTEGER,
    LinkedTableId     VARCHAR(32),
    Sector            VARCHAR(64),
    CONSTRAINT FK_TableType FOREIGN KEY (TypeId) REFERENCES TableType(TypeId),
    CONSTRAINT FK_TableStatus FOREIGN KEY (Status) REFERENCES TableStatus(Status),
    CONSTRAINT FK_LinkedTableId FOREIGN KEY (LinkedTableId) REFERENCES RestaurantTable(TableId),
    CONSTRAINT PK_Table PRIMARY KEY (TableId)
);


--
-- Table TableService:
--   Holds a table service transaction. Each table service transaction in operation has its own table
--   identification attached to it (TableId). 
--   The only constraint is that: The <TableId> may only have one Service
--   'opened' (with the <FinishedTS> unset - NULLed).
--   <NumberOfSeats> set here is the actual number of seats allocated for this transaction.
--
CREATE TABLE TableService (
    ServiceId           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    BusinessPeriod      DATE NOT NULL,
    TableId             VARCHAR(32) NOT NULL,
    StartTS             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FinishedTS          DATETIME,
    UserId							INTEGER NOT NULL,
    NumberOfSeats       INTEGER NOT NULL,
    OrderId             INTEGER,
    TotalAmount         VARCHAR(50),
    LastUpdateTS        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    SourceServiceId     INTEGER,
    CONSTRAINT FK_Table FOREIGN KEY (TableId) REFERENCES RestaurantTable(TableId)
);
CREATE INDEX IDX_TableService_BusinessPeriod ON TableService(BusinessPeriod);
CREATE INDEX IDX_TableService_TableId_FinishTS ON TableService(TableId,FinishedTS);

--
-- Trigger TGR_TableService_LastUpdateTS
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_TableService_LastUpdateTS
AFTER UPDATE ON TableService
 FOR EACH ROW WHEN CURRENT_TIMESTAMP > OLD.LastUpdateTS BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId=NEW.ServiceId; 
END;

--
-- Trigger TGR_RestaurantTable_LastUpdateTS
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_RestaurantTable_LastUpdateTS
AFTER UPDATE ON RestaurantTable
 FOR EACH ROW BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId IN (
				SELECT ServiceId
				  FROM TableService
				 WHERE TableId=(NEW.TableId)
				   AND FinishedTS IS NULL
				 LIMIT 1
		); 
END;


--
-- Table ServiceTenders:
--   Holds the association between the services and the orders tenders.
--
CREATE TABLE ServiceTenders (
		ServiceTenderId     INTEGER NOT NULL,
    ServiceId           INTEGER NOT NULL,
    OrderTenderId       INTEGER NOT NULL,
    OrderId             INTEGER NOT NULL,
    TotalTenderAmount   VARCHAR(50) NOT NULL,
    CONSTRAINT PK_ServiceTenders PRIMARY KEY (ServiceTenderId, ServiceId, OrderTenderId, OrderId)
);

--
-- Trigger TGR_ServiceTenders_LastUpdateTS
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_ServiceTenders_LastUpdateTS
AFTER INSERT ON ServiceTenders
 FOR EACH ROW BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId = NEW.ServiceId; 
END;


--
-- Table ServiceOrders:
--   Holds the association between the services and the orders.
--
CREATE TABLE ServiceOrders (
    ServiceId           INTEGER NOT NULL,
    OrderId             INTEGER NOT NULL,
    POSId               INTEGER NOT NULL,
    State               VARCHAR(64),
    UserId              INTEGER,
    TotalGross          INTEGER,
    CONSTRAINT PK_ServiceOrders PRIMARY KEY (ServiceId, OrderId)
);

--
-- Trigger TGR_ServiceOrders_LastUpdateTS
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_ServiceOrders_LastUpdateTS
AFTER INSERT ON ServiceOrders
 FOR EACH ROW BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId = NEW.ServiceId; 
END;


--
-- Table ServiceSplit:
--   Holds the association between the services and the split orders.
--   This table is only to keep the total service operation persistence.
--
CREATE TABLE ServiceSplit (
    ServiceId           INTEGER NOT NULL,      -- The service identification being split
    SplitKey            VARCHAR(32) NOT NULL,  -- A unique key provided by the API caller
    OrderId             INTEGER NOT NULL,      -- Original OrderId
    LineNumber          INTEGER NOT NULL,      -- The original line number
    SplitOrderId        INTEGER NOT NULL,      -- The new order where the ordered line will be computed
    SplitLineNumber     INTEGER,               -- The new order line
    CONSTRAINT PK_ServiceSplit PRIMARY KEY (ServiceId, SplitKey, OrderId, LineNumber)
);

--
-- Trigger TGR_ServiceSplit_SplitLineNumber
--   Trigger used to calculate the expected line number in the new split order
--
CREATE TRIGGER IF NOT EXISTS TGR_ServiceSplit_SplitLineNumber
AFTER INSERT ON ServiceSplit
 FOR EACH ROW BEGIN
		UPDATE ServiceSplit
		SET SplitLineNumber = (
				SELECT COUNT(1)
				FROM ServiceSplit
				WHERE ServiceId=NEW.ServiceId
		      AND SplitKey=NEW.SplitKey
		      AND SplitOrderId=NEW.SplitOrderId
		)
		WHERE ServiceId=NEW.ServiceId
      AND SplitKey=NEW.SplitKey
      AND OrderId=NEW.OrderId
      AND LineNumber=NEW.LineNumber
      AND SplitOrderId=NEW.SplitOrderId; 
END;


--
-- Table ServiceTip:
--   Holds Tip information for later accounting.
--   It is expected that this data is set prior to tendering the orders.
--
CREATE TABLE ServiceTip (
    ServiceId           INTEGER NOT NULL,      -- The service identification being split
    SplitKey            VARCHAR(32) NOT NULL,  -- A unique key provided by the API caller
    SplitOrderId        INTEGER NOT NULL,      -- The new order where the ordered line will be computed
    TipRate             VARCHAR(50),           -- The Tip rate set for this order
    TipAmount           VARCHAR(50),           -- The Tip amount set for this order
    CalculatedTip       VARCHAR(50),           -- The Tip amount calculated for this order
    CONSTRAINT PK_ServiceTip PRIMARY KEY (ServiceId, SplitKey)
);

--
-- Trigger TGR_ServiceTip_LastUpdateTS
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_ServiceTip_LastUpdateTS
AFTER INSERT ON ServiceTip
 FOR EACH ROW BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId = NEW.ServiceId; 
END;


--
-- Table ServiceCustomProperty:
--   Holds custom parameters per service.
--
CREATE TABLE ServiceCustomProperty (
	ServiceId           INTEGER NOT NULL,
	PropertyKey         VARCHAR(32) NOT NULL,
	PropertyValue       VARCHAR,
	PRIMARY KEY (ServiceId,PropertyKey)
);
CREATE INDEX IDX_ServiceCustomProperty_ServiceId_PropertyKey ON ServiceCustomProperty(ServiceId,PropertyKey);

--
-- Trigger TGR_ServiceCustomProperty_LastUpdateTS_1
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_ServiceCustomProperty_LastUpdateTS_1
AFTER INSERT ON ServiceCustomProperty
 FOR EACH ROW BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId = NEW.ServiceId; 
END;

--
-- Trigger TGR_ServiceCustomProperty_LastUpdateTS_2
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_ServiceCustomProperty_LastUpdateTS_2
AFTER UPDATE ON ServiceCustomProperty
 FOR EACH ROW BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId = NEW.ServiceId; 
END;

--
-- Trigger TGR_ServiceCustomProperty_LastUpdateTS_3
--   Trigger to update last update status of the service.
--
CREATE TRIGGER IF NOT EXISTS TGR_ServiceCustomProperty_LastUpdateTS_3
AFTER DELETE ON ServiceCustomProperty
 FOR EACH ROW BEGIN
		UPDATE TableService
		SET LastUpdateTS = CURRENT_TIMESTAMP
		WHERE ServiceId = OLD.ServiceId; 
END;


--
-- View LatestServicesByTable:
--   Lists the most recent services by <TableId>.
--   It also returns a list of corresponding Orders identification.
--
CREATE VIEW LatestServicesByTable AS
SELECT
    TS.ServiceId                       AS ServiceId,
    TS.BusinessPeriod                  AS BusinessPeriod,
    TS.TableId                         AS TableId,
    TS.StartTS                         AS StartTS,
    TS.FinishedTS                      AS FinishedTS,
    TS.UserId                          AS UserId,
    TS.NumberOfSeats                   AS ServiceSeats,
    TS.OrderId                         AS CurrentOrderId,
    TS.TotalAmount                     AS TotalAmount,
    TS.LastUpdateTS                    AS LastUpdateTS,
    TS.SourceServiceId                 AS SourceServiceId,
    (SELECT T.TableId
       FROM TableService T
 		  WHERE
 		  T.ServiceId=TS.SourceServiceId)  AS SourceTableId,
    (SELECT ('['||GROUP_CONCAT('{"orderId": '||SO.OrderId||', "posId": '||SO.POSId||', "state": '||COALESCE('"'||JSONEscape(SO.State)||'"', 'null')||'}')||']')
     FROM ServiceOrders SO
     WHERE SO.ServiceId=TS.ServiceId
       AND (
       		SO.State IS NULL OR 
       	  SO.State NOT IN (
       						'SYSTEM_VOIDED', 
       						'ABANDONED', 
       						'PAID', 
       						'VOIDED'
       				)
       		)
     )                                 AS Orders,
    (SELECT '['||GROUP_CONCAT('{"orderId": '||SplitOrderId||', "state": "'||State||'"}')||']'
     FROM (
		     SELECT DISTINCT SS.SplitOrderId, COALESCE(SO.State, 'UNDEFINED') AS State
		     FROM ServiceSplit SS
			 LEFT JOIN ServiceOrders SO ON SS.SplitOrderId = SO.OrderId
		     WHERE SS.ServiceId=TS.ServiceId
     )
    ) AS SplitOrders,
		(SELECT ('['||GROUP_CONCAT('"'||T.TableId||'"')||']')
 		 FROM RestaurantTable T
 		 WHERE T.LinkedTableId=TS.TableId) AS LinkedTables,
		(SELECT ('['||GROUP_CONCAT('{"serviceId": '||T.ServiceId||', "tableId": "'||T.TableId||'"}')||']')
 		 FROM TableService T
 		 WHERE T.SourceServiceId=TS.ServiceId) AS SlicedServices
FROM 
    TableService TS
JOIN (
    SELECT
        TableId,
        MAX(ServiceId) AS ServiceId
    FROM
        TableService
    GROUP BY TableId
)   LatestServices
    ON LatestServices.ServiceId=TS.ServiceId;
