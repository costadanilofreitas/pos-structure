-- noinspection SqlNoDataSourceInspectionForFile

-- Schema: fiscal
-- Brief: TaxCalc database definition
-- Created by: ealmeida
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: b923e07dcd2190ab123ff4d4b0a4ddde936ea4cd$" AS Revision;

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

INSERT INTO `Tax` VALUES ('PIS_1,65',2,'PIS',1.65,'P','taxcalculator.ReducedBaseAmountTaxCalculator','ICMS');
INSERT INTO `Tax` VALUES ('PIS_0,65',2,'PIS',1.65,'P','taxcalculator.ReducedBaseAmountTaxCalculator','ICMS');
INSERT INTO `Tax` VALUES ('PIS_0,00',2,'PIS',0,'P','taxcalculator.ReducedBaseAmountTaxCalculator','ICMS');
INSERT INTO `Tax` VALUES ('COFINS_7,60',3,'COFINS',7.6,'C','taxcalculator.ReducedBaseAmountTaxCalculator','ICMS');
INSERT INTO `Tax` VALUES ('COFINS_0,00',3,'COFINS',0,'C','taxcalculator.ReducedBaseAmountTaxCalculator','ICMS');
INSERT INTO `Tax` VALUES ('ICMS_ST',1,'ICMS',0,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_10,20',1,'ICMS',10.2,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_17,00',1,'ICMS',17,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_3,20',1,'ICMS',3.2,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_0,00',1,'ICMS',0,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_2,00',1,'ICMS',2,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_4,00',1,'ICMS',4,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_8,00',1,'ICMS',8,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_6,00',1,'ICMS',6,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_3,00',1,'ICMS',3,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_18,00',1,'ICMS',18,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
INSERT INTO `Tax` VALUES ('ICMS_30,00',1,'ICMS',30,'I','taxcalculator.ReducedBaseAmountTaxCalculator',NULL);
