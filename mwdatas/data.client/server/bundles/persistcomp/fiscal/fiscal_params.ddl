-- Schema: fiscal
-- Brief: FiscalParams database definition
-- Created by: ealmeida
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: 3b0e13fef4f8dfdb0f9157570bfdc6a93a936419$" AS Revision;

CREATE TABLE FiscalParameter (
    ProductCode INTEGER NOT NULL,
	  ParamName VARCHAR NOT NULL,
    ParamValue VARCHAR NOT NULL,
    PRIMARY KEY(ProductCode,ParamName)
);
