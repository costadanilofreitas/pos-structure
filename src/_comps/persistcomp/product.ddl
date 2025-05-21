-- Schema: product
-- Brief: this schema represents the products catalog and all its configuration parameters
-- Created by: amerolli
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author: dcaravana $" AS Author,
       "$Date: 2020-04-30 13:00:00 -0300 (Thu, 30 Apr 2020) $" AS LastModifiedAt,
       "$Revision: g186087f42d58510725f7baba3b9007300000000$" AS Revision;

-- ------------------------- --
-- ------------------------- --
-- Product schema definition --
-- ------------------------- --
-- ------------------------- --

-- -----------------------------------------
-- Main database tables for product catalog
-- -----------------------------------------

CREATE TABLE Product (
    ProductCode     INTEGER NOT NULL,
    ProductName     VARCHAR(50) NOT NULL,
    PRIMARY KEY(ProductCode)
);

CREATE TABLE ProductClassification (
    ClassCode       INTEGER NOT NULL
        CONSTRAINT FK_ProductClassification_ClassCode REFERENCES Product(ProductCode),
    ProductCode     INTEGER NOT NULL
        CONSTRAINT FK_ProductClassification_ProductCode REFERENCES Product(ProductCode),
    PRIMARY KEY(ClassCode, ProductCode)
);

CREATE TABLE ProductPart (
    ProductCode     INTEGER NOT NULL
        CONSTRAINT FK_ProductPart_ProductCode REFERENCES Product(ProductCode),
    PartCode        INTEGER NOT NULL
        CONSTRAINT FK_ProductPart_PartCode REFERENCES Product(ProductCode),
    MinQty          INTEGER NOT NULL DEFAULT 1,
    MaxQty          INTEGER NOT NULL DEFAULT 1,
    DefaultQty      INTEGER NOT NULL DEFAULT 1,
    PartType        INTEGER NOT NULL DEFAULT 0,
    IncludedQty     INTEGER,
    Plain           INTEGER,
    CustomAttr      VARCHAR(1024),
    PRIMARY KEY(ProductCode, PartCode)
);

-- -----------------------------------------
-- Additional tables for QSR implementation
-- -----------------------------------------

CREATE TABLE PromotionOperations AS
    SELECT  0 AS OperId,  'poRegular' AS TypeDescr,     'Add regular item price' AS HelpDescr
    UNION ALL
    SELECT  1 AS OperId,  'poAdd' AS TypeDescr,         'Add the set value' AS HelpDescr
    UNION ALL
    SELECT  2 AS OperId,  'poSub' AS TypeDescr,         'Subtract the set value' AS HelpDescr
    UNION ALL
    SELECT  3 AS OperId,  'poAddItemPerc' AS TypeDescr, 'Add percentage from item price' AS HelpDescr
    UNION ALL
    SELECT  4 AS OperId,  'poSubItemPerc' AS TypeDescr, 'Subtract percentage from item price' AS HelpDescr
    UNION ALL
    SELECT  5 AS OperId,  'poUpCharge' AS TypeDescr,    'Up charge item price by set value' AS HelpDescr
    UNION ALL
    SELECT  6 AS OperId,  'poDownCharge' AS TypeDescr,  'Down charge item price by set value' AS HelpDescr
    UNION ALL
    SELECT  7 AS OperId,  'poNoPrice' AS TypeDescr,     'Item is free of charge' AS HelpDescr
    UNION ALL
    SELECT  8 AS OperId,  'poSepSold' AS TypeDescr,     'Sold separetely by item price' AS HelpDescr
    UNION ALL
    SELECT  9 AS OperId,  'poSepSoldValue' AS TypeDescr,'Sold separetely by set value' AS HelpDescr
    UNION ALL
    SELECT  10 AS OperId, 'poExist' AS TypeDescr,       'Item must exist on sale' AS HelpDescr
    UNION ALL
    SELECT  11 AS OperId, 'poAddSalePerc' AS TypeDescr, 'Add percentage of sale total' AS HelpDescr
    UNION ALL
    SELECT  12 AS OperId, 'poSubSalePerc' AS TypeDescr, 'Subtract percentage of sale total' AS HelpDescr;

CREATE TABLE PromoRule (
    PromoCode       INTEGER NOT NULL,
    SetCode         INTEGER NOT NULL,
    PromoOptIdx     INTEGER,
    PromoPartIdx    INTEGER NOT NULL,
    Qty             INTEGER NOT NULL,
    PromoOperation  INTEGER NOT NULL
        CONSTRAINT FK_PromoPartRule_PromoOperation REFERENCES PromotionOperations(OperId),
    RuleValue       VARCHAR(30) NOT NULL DEFAULT('0.00'),
    PRIMARY KEY(PromoCode,SetCode,PromoOptIdx,PromoPartIdx)
);

CREATE TABLE ModifierQtyLabels (
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ModifierQtyDescr_ProductCode REFERENCES Product(ProductCode),
    Qty INTEGER NOT NULL,
    Label VARCHAR(50) NOT NULL,
    PRIMARY KEY(ProductCode,Qty)
);

CREATE TABLE Dimensions (
    DimChar CHAR(1) NOT NULL,
    DimPrio INTEGER NOT NULL,
    DimDescr VARCHAR(64),
    PRIMARY KEY (DimChar)
);

CREATE TABLE DimensionGroups (
    DimGroupId INTEGER NOT NULL,
    DimChar CHAR(1) NOT NULL
        CONSTRAINT FK_DimensionGroups_DimChar REFERENCES Dimensions(DimChar),
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_DimensionGroups_ProductCode REFERENCES Product(ProductCode),
    PRIMARY KEY(DimGroupId,DimChar,ProductCode)
);

CREATE TABLE Descriptions (
    DescrId INTEGER NOT NULL,
    Description VARCHAR(50) NOT NULL,
    Language VARCHAR(5),
    PRIMARY KEY(DescrId)
);

CREATE TABLE ProductDescriptions (
    DescrId INTEGER NOT NULL
        CONSTRAINT FK_ProductDescriptions_DescrId REFERENCES Descriptions(DescrId),
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ProductDescriptions_ProductCode REFERENCES Product(ProductCode),
    ProductDescription VARCHAR(64) NOT NULL,
    PRIMARY KEY(DescrId, ProductCode)
);

CREATE TABLE ProductType (
    TypeId INTEGER NOT NULL,
    TypeDescr VARCHAR(50) NOT NULL,
    PRIMARY KEY (TypeId)
);

INSERT OR REPLACE INTO ProductType(TypeId,TypeDescr)
    SELECT 0 AS TypeId, 'TYPE_REGULAR' AS TypeDescr
    UNION ALL
    SELECT 1 AS TypeId, 'TYPE_OPTION' AS TypeDescr
    UNION ALL
    SELECT 2 AS TypeId, 'TYPE_COMBO' AS TypeDescr
    UNION ALL
    SELECT 3 AS TypeId, 'TYPE_MENU' AS TypeDescr
    UNION ALL
    SELECT 4 AS TypeId, 'TYPE_SET' AS TypeDescr
    UNION ALL
    SELECT 5 AS TypeId, 'TYPE_PROMO' AS TypeDescr
    UNION ALL
    SELECT 6 AS TypeId, 'TYPE_COUPON' AS TypeDescr;

CREATE TABLE ProductKernelParams (
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ProductKernelParams_ProductCode REFERENCES Product(ProductCode),
    ProductType INTEGER NOT NULL DEFAULT 0
        CONSTRAINT FK_ProductKernelParams_ProductType REFERENCES ProductType(TypeId),
    Enabled INTEGER NOT NULL DEFAULT 1,
    ProductPriority INTEGER NOT NULL DEFAULT 100,
    PromoSortMode INTEGER NOT NULL DEFAULT 2,
    MeasureUnit VARCHAR(5),
    SysProdExplosionActive INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY(ProductCode)
);

CREATE TRIGGER TGProductKernelParamsInsert
AFTER INSERT ON Product
FOR EACH ROW WHEN ((SELECT COUNT(ProductCode) FROM ProductKernelParams WHERE ProductCode=NEW.ProductCode) = 0)
BEGIN
    INSERT INTO ProductKernelParams(ProductCode) VALUES(NEW.ProductCode);
END;

CREATE TABLE ProductCustomParams (
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ProductCustomParams_ProductCode REFERENCES Product(ProductCode),
    CustomParamId VARCHAR(50) NOT NULL,
    CustomParamValue VARCHAR,
    PRIMARY KEY(ProductCode,CustomParamId)
);

CREATE TABLE ProductTags (
    Tag VARCHAR(64) NOT NULL,
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ProductTags_ProductCode REFERENCES Product(ProductCode),
    PRIMARY KEY(Tag, ProductCode)
);
CREATE INDEX IDX_ProductTags_Tag ON ProductTags(Tag);
CREATE INDEX IDX_ProductTags_ProductCode ON ProductTags(ProductCode);

CREATE TABLE ProductXREF (
    Context VARCHAR(64),
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ProductXREF_ProductCode REFERENCES Product(ProductCode),
    SimilarCode INTEGER NOT NULL,
    Description VARCHAR(1024),
    Enabled INTEGER,
    PRIMARY KEY(Context, ProductCode, SimilarCode)
);
CREATE INDEX IDX_ProductXREF_SimilarCode ON ProductXREF(SimilarCode);


-- -------------------------
-- Product Navigation
-- -------------------------
CREATE TABLE Navigation (
    NavId       INTEGER PRIMARY KEY NOT NULL,
    Name        VARCHAR(256) NOT NULL,
    ParentNavId INTEGER,
    SortOrder   INTEGER,
    ButtonText  VARCHAR(256),
    ButtonColor CHAR(6)
);

CREATE TABLE NavigationDescriptions (
    DescrId INTEGER NOT NULL
        CONSTRAINT FK_NavigationDescriptions_DescrId REFERENCES Descriptions(DescrId),
    NavId INTEGER NOT NULL
        CONSTRAINT FK_NavigationDescriptions_NavId REFERENCES Navigation(NavId),
    NavigationDescription VARCHAR(64) NOT NULL,
    PRIMARY KEY(DescrId, NavId)
);

CREATE TABLE NavigationCustomParams (
    NavId INTEGER NOT NULL
        CONSTRAINT FK_NavigationCustomParams_NavId REFERENCES NavId(Navigation),
    CustomParamId VARCHAR(50) NOT NULL,
    CustomParamValue VARCHAR,
    PRIMARY KEY(NavId, CustomParamId)
);

CREATE TABLE ProductNavigation (
    NavId INTEGER NOT NULL
        CONSTRAINT FK_ProductNavigation_NavId REFERENCES NavId(Navigation),
    ClassCode INTEGER NOT NULL,
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ProductNavigation_ProductCode REFERENCES Product(ProductCode),
    PRIMARY KEY(NavId, ClassCode, ProductCode)
);

CREATE TABLE ProductNavigationCustomParams (
    NavId INTEGER NOT NULL
        CONSTRAINT FK_ProductNavigationCustomParams_NavId REFERENCES NavId(Navigation),
    ClassCode INTEGER NOT NULL,
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_ProductNavigationCustomParams_ProductCode REFERENCES Product(ProductCode),
    CustomParamId VARCHAR(50) NOT NULL,
    CustomParamValue VARCHAR,
    PRIMARY KEY(NavId, ClassCode, ProductCode, CustomParamId)
);

-- -------------------------
-- Prices schema definition
-- -------------------------

CREATE TABLE PriceList (
    PriceListId VARCHAR(8) NOT NULL,
    MenuPriceBasis CHAR(1) NOT NULL DEFAULT 'G',
    EnabledFrom DATETIME NOT NULL,
    EnabledThru DATETIME NOT NULL,
    PRIMARY KEY(PriceListId)
);

CREATE TABLE Price (
    PriceKey INTEGER PRIMARY KEY AUTOINCREMENT,
    PriceListId VARCHAR(8) NOT NULL
        CONSTRAINT FK_Price_PriceListId REFERENCES PriceList(PriceListId),
    ProductCode INTEGER NOT NULL
        CONSTRAINT FK_Price_ProductCode REFERENCES Product(ProductCode),
    Context VARCHAR(50),
    DefaultUnitPrice VARCHAR(30),
    AddedUnitPrice VARCHAR(30),
    SubtractedUnitPrice VARCHAR(30),
    Computed SMALLINT DEFAULT 1,
    IncludedQty INTEGER,
    ValidFrom DATETIME,
    ValidThru DATETIME
);

CREATE INDEX IDX_Price_ProductCode ON Price(ProductCode);

-- ----------------------------------------
-- Production information schema definition
-- ----------------------------------------

CREATE TABLE Production (
    ProductCode INTEGER PRIMARY KEY
        CONSTRAINT FK_Production_ProductCode REFERENCES Product(ProductCode),
    JITLines VARCHAR(50),
    ShowOnKitchen SMALLINT DEFAULT 0,
    Expiration INT
);

-- ----------------------
-- Tender schema
-- ----------------------

CREATE TABLE Currency (
    CurrencyCode        CHAR(3) NOT NULL,
    OriginalCountry     VARCHAR(50),
    CurrencyName        VARCHAR(50),
    SymbolUnicode       VARCHAR(50),
    PRIMARY KEY(CurrencyCode)
);

-- --------------------------
-- Currently known currencies
-- --------------------------
BEGIN TRANSACTION;
INSERT INTO Currency VALUES('BRL','Brazil','Brazil Real','82,36');
INSERT INTO Currency VALUES('USD','United States of America','Dollars','36');
COMMIT TRANSACTION;

CREATE TABLE CurrencyExchange (
    ExchangeRateId      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    CurrencyFrom        CHAR(3) NOT NULL
        CONSTRAINT FK_CurrencyExchange_CurrencyFrom REFERENCES Currency(CurrencyCode),
    CurrencyTo          CHAR(3) NOT NULL
        CONSTRAINT FK_CurrencyExchange_CurrencyTo REFERENCES Currency(CurrencyCode),
    RateAmount          VARCHAR(30) NOT NULL,
    RoundingMode        INTEGER NOT NULL DEFAULT 0,
    RoundingScale       INTEGER NOT NULL DEFAULT 2,
    ValidFrom           DATE NOT NULL,
    ValidThru           DATE NOT NULL
);

CREATE TABLE TenderElectronicType (
    TypeId              INTEGER NOT NULL,
    TypeDescr           VARCHAR(50) NOT NULL,
    PRIMARY KEY(TypeId)
);

CREATE TABLE TenderType (
    TenderId          INTEGER NOT NULL,
    TenderDescr       CHAR(32) NOT NULL,
    TenderCurrency    CHAR(3) NOT NULL
        CONSTRAINT FK_TenderType_Currency REFERENCES Currency(CurrencyCode),
    TenderIdForChange INTEGER,
    KeepExcess        INTEGER NOT NULL DEFAULT 0,
    SkimLimit         VARCHAR(30),
    ChangeLimit       VARCHAR(30),
    ElectronicType    INTEGER NOT NULL DEFAULT 0
        CONSTRAINT FK_TenderType_ElectronicType REFERENCES TenderElectronicType(TypeId),
    OpenDrawer        INTEGER NOT NULL DEFAULT 1,
    NeedAuth          INTEGER NOT NULL DEFAULT 0,
    ParentTenderId    INTEGER,
    PRIMARY KEY(TenderId)
);

-- --------------------------------
-- Possible electronic tender types
-- --------------------------------
INSERT INTO TenderElectronicType(TypeId,TypeDescr) VALUES(0, 'NON_ELECTRONIC');
INSERT INTO TenderElectronicType(TypeId,TypeDescr) VALUES(1, 'CREDIT_CARD');
INSERT INTO TenderElectronicType(TypeId,TypeDescr) VALUES(2, 'DEBIT_CARD');
INSERT INTO TenderElectronicType(TypeId,TypeDescr) VALUES(9, 'OTHER');

-- -------------------------
-- Views definition
-- -------------------------

CREATE VIEW ProductDimensions AS
SELECT DG1.DimGroupId AS DimGroupId,
       DG1.ProductCode AS ProductCode,
       DG2.DimChar AS DimChar,
       D.DimPrio AS DimPrio,
       DG2.ProductCode AS DimPCode
FROM DimensionGroups DG1
JOIN DimensionGroups DG2 ON DG2.DimGroupId=DG1.DimGroupId
JOIN Dimensions D ON D.DimChar=DG2.DimChar
ORDER BY ProductCode, DimPrio;

CREATE VIEW ProductSets AS
SELECT
      ProductClassification.ProductCode AS ProductCode,
      ProductType.TypeDescr AS ProductType,
      Product.ProductName AS ProductName,
      GROUP_CONCAT(Sets.ProductName) AS Sets,
      GROUP_CONCAT(Sets.ProductCode) AS SetCodes
FROM
    ProductClassification
JOIN
    Product
    ON Product.ProductCode=ProductClassification.ProductCode
JOIN
    ProductKernelParams
    ON ProductKernelParams.ProductCode=ProductClassification.ProductCode
JOIN
    ProductType
    ON ProductType.TypeId=ProductKernelParams.ProductType
JOIN
    (
        SELECT
            Product.*
        FROM
            Product
        JOIN
            ProductKernelParams
            ON ProductKernelParams.ProductCode=Product.ProductCode
        JOIN
            ProductType
            ON ProductType.TypeId=ProductKernelParams.ProductType
        WHERE
            ProductType.TypeDescr='TYPE_SET'
    ) Sets
    ON Sets.ProductCode=ProductClassification.ClassCode
GROUP BY ProductClassification.ProductCode;

CREATE VIEW ProductPromos AS
SELECT
    R.PromoCode AS PromoCode,
    P.ProductPriority AS Priority,
    P.PromoSortMode AS SortMode,
    P.Enabled AS Enabled,
    S.ProductName AS SetName,
    R.SetCode AS SetCode,
    R.PromoOptIdx AS PromoOpt,
    R.PromoPartIdx AS PromoPart,
    R.Qty AS Qty,
    R.PromoOperation AS Oper,
    R.RuleValue AS Value
FROM
    PromoRule R
JOIN
    Product S
    ON S.ProductCode=R.SetCode
JOIN
    ProductKernelParams P
    ON P.ProductCode=R.PromoCode
ORDER BY Priority,PromoCode,PromoPart,PromoOpt;

-- -----------------------------------------------------------------
-- Triggers to Identify Changes in the Product Catalog Configuration
-- -----------------------------------------------------------------

CREATE TABLE ProductCatalogChangesCounter (
    ChangesCount        INTEGER,
    ChangesDateTime     DATETIME
);
INSERT INTO ProductCatalogChangesCounter VALUES(0, CURRENT_TIMESTAMP);
-- Product
CREATE TRIGGER TG_ProductChanges_1 AFTER DELETE ON Product BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_ProductChanges_2 AFTER UPDATE ON Product BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_ProductChanges_3 AFTER INSERT ON Product BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
-- ProductPart
CREATE TRIGGER TG_ProductPartChanges_1 AFTER DELETE ON ProductPart BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_ProductPartChanges_2 AFTER UPDATE ON ProductPart BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_ProductPartChanges_3 AFTER INSERT ON ProductPart BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
-- ProductClassfication
CREATE TRIGGER TG_ProductClassificationChanges_1 AFTER DELETE ON ProductClassification BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_ProductClassificationChanges_2 AFTER UPDATE ON ProductClassification BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_ProductClassificationChanges_3 AFTER INSERT ON ProductClassification BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
-- PriceList
CREATE TRIGGER TG_PriceListChanges_1 AFTER DELETE ON PriceList BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_PriceListChanges_2 AFTER UPDATE ON PriceList BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_PriceListChanges_3 AFTER INSERT ON PriceList BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
-- Price
CREATE TRIGGER TG_PriceChanges_1 AFTER DELETE ON Price BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_PriceChanges_2 AFTER UPDATE ON Price BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_PriceChanges_3 AFTER INSERT ON Price BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
-- Dimensions
CREATE TRIGGER TG_DimensionsChanges_1 AFTER DELETE ON Dimensions BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_DimensionsChanges_2 AFTER UPDATE ON Dimensions BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_DimensionsChanges_3 AFTER INSERT ON Dimensions BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
-- DimensionGroups
CREATE TRIGGER TG_DimensionGroupsChanges_1 AFTER DELETE ON DimensionGroups BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_DimensionGroupsChanges_2 AFTER UPDATE ON DimensionGroups BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;
CREATE TRIGGER TG_DimensionGroupsChanges_3 AFTER INSERT ON DimensionGroups BEGIN UPDATE ProductCatalogChangesCounter SET ChangesCount=ChangesCount+1,ChangesDateTime=CURRENT_TIMESTAMP; END;

-- -----------------------------------
-- Triggers for constraint validation
-- -----------------------------------

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductClassification_ClassCode_Product_ProductCode
BEFORE INSERT ON [ProductClassification]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductClassification" violates foreign key constraint "fki_ProductClassification_ClassCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ClassCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductClassification_ClassCode_Product_ProductCode
BEFORE UPDATE ON [ProductClassification]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductClassification" violates foreign key constraint "fku_ProductClassification_ClassCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ClassCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductClassification_ClassCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductClassification_ClassCode_Product_ProductCode"')
        WHERE (SELECT ClassCode FROM ProductClassification WHERE ClassCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductClassification_ProductCode_Product_ProductCode
BEFORE INSERT ON [ProductClassification]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductClassification" violates foreign key constraint "fki_ProductClassification_ProductCode_Product_ProductCode"')
       WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductClassification_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ProductClassification]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductClassification" violates foreign key constraint "fku_ProductClassification_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductClassification_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductClassification_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ProductClassification WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductPart_ProductCode_Product_ProductCode
BEFORE INSERT ON [ProductPart]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductPart" violates foreign key constraint "fki_ProductPart_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductPart_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ProductPart]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductPart" violates foreign key constraint "fku_ProductPart_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductPart_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductPart_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ProductPart WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductPart_PartCode_Product_ProductCode
BEFORE INSERT ON [ProductPart]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductPart" violates foreign key constraint "fki_ProductPart_PartCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.PartCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductPart_PartCode_Product_ProductCode
BEFORE UPDATE ON [ProductPart]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductPart" violates foreign key constraint "fku_ProductPart_PartCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.PartCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductPart_PartCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductPart_PartCode_Product_ProductCode"')
        WHERE (SELECT PartCode FROM ProductPart WHERE PartCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ModifierQtyLabels_ProductCode_Product_ProductCode
BEFORE INSERT ON [ModifierQtyLabels]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ModifierQtyLabels" violates foreign key constraint "fki_ModifierQtyLabels_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ModifierQtyLabels_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ModifierQtyLabels]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ModifierQtyLabels" violates foreign key constraint "fku_ModifierQtyLabels_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ModifierQtyLabels_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ModifierQtyLabels_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ModifierQtyLabels WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_DimensionGroups_DimChar_Dimensions_DimChar
BEFORE INSERT ON [DimensionGroups]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "DimensionGroups" violates foreign key constraint "fki_DimensionGroups_DimChar_Dimensions_DimChar"')
        WHERE (SELECT DimChar FROM Dimensions WHERE DimChar = NEW.DimChar) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_DimensionGroups_DimChar_Dimensions_DimChar
BEFORE UPDATE ON [DimensionGroups]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "DimensionGroups" violates foreign key constraint "fku_DimensionGroups_DimChar_Dimensions_DimChar"')
        WHERE (SELECT DimChar FROM Dimensions WHERE DimChar = NEW.DimChar) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_DimensionGroups_DimChar_Dimensions_DimChar
BEFORE DELETE ON Dimensions
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Dimensions" violates foreign key constraint "fkd_DimensionGroups_DimChar_Dimensions_DimChar"')
        WHERE (SELECT DimChar FROM DimensionGroups WHERE DimChar = OLD.DimChar) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_DimensionGroups_ProductCode_Product_ProductCode
BEFORE INSERT ON [DimensionGroups]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "DimensionGroups" violates foreign key constraint "fki_DimensionGroups_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_DimensionGroups_ProductCode_Product_ProductCode
BEFORE UPDATE ON [DimensionGroups]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "DimensionGroups" violates foreign key constraint "fku_DimensionGroups_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_DimensionGroups_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_DimensionGroups_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM DimensionGroups WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductDescriptions_DescrId_Descriptions_DescrId
BEFORE INSERT ON [ProductDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductDescriptions" violates foreign key constraint "fki_ProductDescriptions_DescrId_Descriptions_DescrId"')
        WHERE (SELECT DescrId FROM Descriptions WHERE DescrId = NEW.DescrId) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductDescriptions_DescrId_Descriptions_DescrId
BEFORE UPDATE ON [ProductDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductDescriptions" violates foreign key constraint "fku_ProductDescriptions_DescrId_Descriptions_DescrId"')
        WHERE (SELECT DescrId FROM Descriptions WHERE DescrId = NEW.DescrId) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductDescriptions_DescrId_Descriptions_DescrId
BEFORE DELETE ON Descriptions
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Descriptions" violates foreign key constraint "fkd_ProductDescriptions_DescrId_Descriptions_DescrId"')
        WHERE (SELECT DescrId FROM ProductDescriptions WHERE DescrId = OLD.DescrId) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductDescriptions_ProductCode_Product_ProductCode
BEFORE INSERT ON [ProductDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductDescriptions" violates foreign key constraint "fki_ProductDescriptions_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductDescriptions_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ProductDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductDescriptions" violates foreign key constraint "fku_ProductDescriptions_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductDescriptions_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductDescriptions_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ProductDescriptions WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_NavigationDescriptions_DescrId_Descriptions_DescrId
BEFORE INSERT ON [NavigationDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "NavigationDescriptions" violates foreign key constraint "fki_NavigationDescriptions_DescrId_Descriptions_DescrId"')
        WHERE (SELECT DescrId FROM Descriptions WHERE DescrId = NEW.DescrId) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_NavigationDescriptions_DescrId_Descriptions_DescrId
BEFORE UPDATE ON [NavigationDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "NavigationDescriptions" violates foreign key constraint "fku_NavigationDescriptions_DescrId_Descriptions_DescrId"')
        WHERE (SELECT DescrId FROM Descriptions WHERE DescrId = NEW.DescrId) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_NavigationDescriptions_DescrId_Descriptions_DescrId
BEFORE DELETE ON Descriptions
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Descriptions" violates foreign key constraint "fkd_NavigationDescriptions_DescrId_Descriptions_DescrId"')
        WHERE (SELECT DescrId FROM NavigationDescriptions WHERE DescrId = OLD.DescrId) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_NavigationDescriptions_NavId_Navigation_NavId
BEFORE INSERT ON [NavigationDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "NavigationDescriptions" violates foreign key constraint "fki_NavigationDescriptions_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM Navigation WHERE NavId = NEW.NavId) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_NavigationDescriptions_NavId_Navigation_NavId
BEFORE UPDATE ON [NavigationDescriptions]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "NavigationDescriptions" violates foreign key constraint "fku_NavigationDescriptions_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM Navigation WHERE NavId = NEW.NavId) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_NavigationDescriptions_NavId_Navigation_NavId
BEFORE DELETE ON Navigation
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Navigation" violates foreign key constraint "fkd_NavigationDescriptions_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM NavigationDescriptions WHERE NavId = OLD.NavId) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductKernelParams_ProductCode_Product_ProductCode
BEFORE INSERT ON [ProductKernelParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductKernelParams" violates foreign key constraint "fki_ProductKernelParams_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductKernelParams_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ProductKernelParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductKernelParams" violates foreign key constraint "fku_ProductKernelParams_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductKernelParams_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductKernelParams_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ProductKernelParams WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductKernelParams_ProductType_ProductType_TypeId
BEFORE INSERT ON [ProductKernelParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductKernelParams" violates foreign key constraint "fki_ProductKernelParams_ProductType_ProductType_TypeId"')
        WHERE (SELECT TypeId FROM ProductType WHERE TypeId = NEW.ProductType) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductKernelParams_ProductType_ProductType_TypeId
BEFORE UPDATE ON [ProductKernelParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductKernelParams" violates foreign key constraint "fku_ProductKernelParams_ProductType_ProductType_TypeId"')
        WHERE (SELECT TypeId FROM ProductType WHERE TypeId = NEW.ProductType) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductKernelParams_ProductType_ProductType_TypeId
BEFORE DELETE ON ProductType
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "ProductType" violates foreign key constraint "fkd_ProductKernelParams_ProductType_ProductType_TypeId"')
        WHERE (SELECT ProductType FROM ProductKernelParams WHERE ProductType = OLD.TypeId) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductCustomParams_ProductCode_Product_ProductCode
BEFORE INSERT ON [ProductCustomParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductCustomParams" violates foreign key constraint "fki_ProductCustomParams_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductCustomParams_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ProductCustomParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductCustomParams" violates foreign key constraint "fku_ProductCustomParams_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductCustomParams_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductCustomParams_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ProductCustomParams WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_NavigationCustomParams_NavId_Navigation_NavId
BEFORE INSERT ON [NavigationCustomParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "NavigationCustomParams" violates foreign key constraint "fki_NavigationCustomParams_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM Navigation WHERE NavId = NEW.NavId) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_NavigationCustomParams_NavId_Navigation_NavId
BEFORE UPDATE ON [NavigationCustomParams]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "NavigationCustomParams" violates foreign key constraint "fku_NavigationCustomParams_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM Navigation WHERE NavId = NEW.NavId) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_NavigationCustomParams_NavId_Navigation_NavId
BEFORE DELETE ON Navigation
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Navigation" violates foreign key constraint "fkd_NavigationCustomParams_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM NavigationCustomParams WHERE NavId = OLD.NavId) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductNavigation_NavId_Navigation_NavId
BEFORE INSERT ON [ProductNavigation]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductNavigation" violates foreign key constraint "fki_ProductNavigation_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM Navigation WHERE NavId = NEW.NavId) IS NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductNavigation_ProductCode_Product_ProductCode
BEFORE INSERT ON [ProductNavigation]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductNavigation" violates foreign key constraint "fki_ProductNavigation_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductNavigation_NavId_Navigation_NavId
BEFORE UPDATE ON [ProductNavigation]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductNavigation" violates foreign key constraint "fku_ProductNavigation_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM Navigation WHERE NavId = NEW.NavId) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductNavigation_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ProductNavigation]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductNavigation" violates foreign key constraint "fku_ProductNavigation_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductNavigation_NavId_Navigation_NavId
BEFORE DELETE ON Navigation
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Navigation" violates foreign key constraint "fkd_ProductNavigation_NavId_Navigation_NavId"')
        WHERE (SELECT NavId FROM ProductNavigation WHERE NavId = OLD.NavId) IS NOT NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductNavigation_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductNavigation_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ProductNavigation WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_ProductTags_ProductCode_Product_ProductCode
BEFORE INSERT ON [ProductTags]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "ProductTags" violates foreign key constraint "fki_ProductTags_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_ProductTags_ProductCode_Product_ProductCode
BEFORE UPDATE ON [ProductTags]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "ProductTags" violates foreign key constraint "fku_ProductTags_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_ProductTags_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_ProductTags_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM ProductTags WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_Price_PriceListId_PriceList_PriceListId
BEFORE INSERT ON [Price]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "Price" violates foreign key constraint "fki_Price_PriceListId_PriceList_PriceListId"')
        WHERE (SELECT PriceListId FROM PriceList WHERE PriceListId = NEW.PriceListId) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_Price_PriceListId_PriceList_PriceListId
BEFORE UPDATE ON [Price]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "Price" violates foreign key constraint "fku_Price_PriceListId_PriceList_PriceListId"')
        WHERE (SELECT PriceListId FROM PriceList WHERE PriceListId = NEW.PriceListId) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_Price_PriceListId_PriceList_PriceListId
BEFORE DELETE ON PriceList
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "PriceList" violates foreign key constraint "fkd_Price_PriceListId_PriceList_PriceListId"')
        WHERE (SELECT PriceListId FROM Price WHERE PriceListId = OLD.PriceListId) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_Price_ProductCode_Product_ProductCode
BEFORE INSERT ON [Price]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "Price" violates foreign key constraint "fki_Price_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_Price_ProductCode_Product_ProductCode
BEFORE UPDATE ON [Price]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "Price" violates foreign key constraint "fku_Price_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_Price_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_Price_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Price WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_Production_ProductCode_Product_ProductCode
BEFORE INSERT ON [Production]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'insert on table "Production" violates foreign key constraint "fki_Production_ProductCode_Product_ProductCode"')
        WHERE NEW.ProductCode IS NOT NULL AND (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_Production_ProductCode_Product_ProductCode
BEFORE UPDATE ON [Production]
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'update on table "Production" violates foreign key constraint "fku_Production_ProductCode_Product_ProductCode"')
        WHERE NEW.ProductCode IS NOT NULL AND (SELECT ProductCode FROM Product WHERE ProductCode = NEW.ProductCode) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_Production_ProductCode_Product_ProductCode
BEFORE DELETE ON Product
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, 'delete on table "Product" violates foreign key constraint "fkd_Production_ProductCode_Product_ProductCode"')
        WHERE (SELECT ProductCode FROM Production WHERE ProductCode = OLD.ProductCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_TenderType_TenderCurrency_Currency_CurrencyCode
BEFORE INSERT ON [TenderType]
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'insert on table "TenderType" violates foreign key constraint "fki_TenderType_TenderCurrency_Currency_CurrencyCode"')
        WHERE (SELECT CurrencyCode FROM Currency WHERE CurrencyCode = NEW.TenderCurrency) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_TenderType_TenderCurrency_Currency_CurrencyCode
BEFORE UPDATE ON [TenderType]
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "TenderType" violates foreign key constraint "fku_TenderType_TenderCurrency_Currency_CurrencyCode"')
        WHERE (SELECT CurrencyCode FROM Currency WHERE CurrencyCode = NEW.TenderCurrency) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_TenderType_TenderCurrency_Currency_CurrencyCode
BEFORE DELETE ON Currency
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'delete on table "Currency" violates foreign key constraint "fkd_TenderType_TenderCurrency_Currency_CurrencyCode"')
        WHERE (SELECT TenderCurrency FROM TenderType WHERE TenderCurrency = OLD.CurrencyCode) IS NOT NULL;
END;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_TenderType_ElectronicType_TenderElectronicType_TypeId
BEFORE INSERT ON [TenderType]
FOR EACH ROW BEGIN
  SELECT RAISE(ROLLBACK, 'insert on table "TenderType" violates foreign key constraint "fki_TenderType_ElectronicType_TenderElectronicType_TypeId"')
  WHERE (SELECT TypeId FROM TenderElectronicType WHERE TypeId = NEW.ElectronicType) IS NULL;
END;

-- Foreign key preventing update
CREATE TRIGGER fku_TenderType_ElectronicType_TenderElectronicType_TypeId
BEFORE UPDATE ON [TenderType]
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "TenderType" violates foreign key constraint "fku_TenderType_ElectronicType_TenderElectronicType_TypeId"')
        WHERE (SELECT TypeId FROM TenderElectronicType WHERE TypeId = NEW.ElectronicType) IS NULL;
END;

-- Foreign key preventing delete
CREATE TRIGGER fkd_TenderType_ElectronicType_TenderElectronicType_TypeId
BEFORE DELETE ON TenderElectronicType
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'delete on table "TenderElectronicType" violates foreign key constraint "fkd_TenderType_ElectronicType_TenderElectronicType_TypeId"')
        WHERE (SELECT ElectronicType FROM TenderType WHERE ElectronicType = OLD.TypeId) IS NOT NULL;
END;
