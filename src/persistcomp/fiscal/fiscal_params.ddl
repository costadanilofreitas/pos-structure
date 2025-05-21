-- noinspection SqlNoDataSourceInspectionForFile

-- Schema: fiscal
-- Brief: FiscalParams database definition
-- Created by: ealmeida
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: a0e3132e0b163fa7e79b822d909f26e63493a74d$" AS Revision;

CREATE TABLE FiscalParameter (
    ProductCode INTEGER NOT NULL,
    ParamName VARCHAR NOT NULL,
    ParamValue VARCHAR NOT NULL,
    PRIMARY KEY(ProductCode,ParamName)
);
