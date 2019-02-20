-- Schema: fiscal
-- Brief: TaxCalc database definition
-- Created by: ealmeida
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: 04e93e0c6f6e0377f0191dab4db233a98acb7e87$" AS Revision;

CREATE TABLE Tax (
    Code VARCHAR NOT NULL,
	  TaxOrder INTEGER NOT NULL,
    Name VARCHAR NOT NULL,
    Rate NUMBER NOT NULL,
    FiscalIndex VARCHAR NOT NULL,
	  TaxProcessor VARCHAR NOT NULL,
	  Parameters VARCHAR,
    PRIMARY KEY(Code)
);

CREATE TABLE ProductTax (
    ProductCode INTEGER NOT NULL,
    TaxCode VARCHAR NOT NULL
		CONSTRAINT FK_ProductTax_Tax REFERENCES Tax(Code),
    PRIMARY KEY(ProductCode,TaxCode)
);
