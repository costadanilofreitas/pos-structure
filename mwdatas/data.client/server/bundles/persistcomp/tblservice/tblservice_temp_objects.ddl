-- --------------------------------------------------------------------------------
-- Copyright (C) 2018 MWneo Corporation
-- Copyright (C) 2018 Omega Tech Enterprises Ltd. 
-- (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
--
-- Author: amerolli
--
-- Table Service temporary database objects.
-- --------------------------------------------------------------------------------

CREATE TEMPORARY TABLE TSMemory (
		MemKey		VARCHAR,
		MemValue	VARCHAR,
		PRIMARY KEY (MemKey)
);

---
--- Temporary table used for SPLICE_SERVICE API
---
CREATE TEMPORARY TABLE SlicedService (
    ServiceId           INTEGER NOT NULL,      -- The service identification result of the slice
    OrderId             INTEGER NOT NULL,      -- Original OrderId
    LineNumber          INTEGER NOT NULL,      -- The original line number
    SliceLineNumber     INTEGER,               -- The new order line
    CONSTRAINT PK_SlicedService PRIMARY KEY (ServiceId, OrderId, LineNumber)
);
