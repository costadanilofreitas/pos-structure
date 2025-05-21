-- noinspection SqlNoDataSourceInspectionForFile

-- Schema: product
-- Brief: Create a temporary table for SYSPROD schema update
-- Created by: amerolli
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TEMPORARY TABLE CheckCatalogChanges (
	SchemaRevision		VARCHAR(50),
	ChangesCounter		INTEGER,
	ChangesDateTime		DATETIME
);

-- Get current SYSPROD schema state.
INSERT INTO CheckCatalogChanges
SELECT SchemaRevision, ChangesCounter, ChangesDateTime
FROM sysproddb.ProductCatalogChanges;

CREATE TEMPORARY TABLE BaseProductTree ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level0 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level1 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level2 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level3 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level4 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level5 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level6 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE BaseProductTree_level7 ( 
	ItemId VARCHAR(50) NOT NULL, 
	ProductCode INTEGER NOT NULL, 
	IsClass INTEGER NOT NULL DEFAULT 0, 
	PartCode INTEGER, 
	RecursionLevel INTEGER, 
	MenuItem INTEGER
);

CREATE TEMPORARY TABLE SYSPROD_Params AS
SELECT CAST(6 AS INTEGER) AS MaxLevel;

CREATE TEMPORARY VIEW ProductTreeView AS
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level0 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params) UNION ALL
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level1 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params) UNION ALL
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level2 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params) UNION ALL
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level3 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params) UNION ALL
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level4 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params) UNION ALL
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level5 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params) UNION ALL
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level6 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params) UNION ALL
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree_level7 WHERE RecursionLevel<=(SELECT MaxLevel FROM SYSPROD_Params);

-- Create a temporary trigger for the SYSPROD schema update
-- This implements all the SYSPROD schema update logic.
CREATE TEMPORARY TRIGGER TriggerCheckCatalogChanges AFTER UPDATE ON CheckCatalogChanges
	WHEN (OLD.SchemaRevision!=NEW.SchemaRevision OR OLD.ChangesCounter!=NEW.ChangesCounter OR OLD.ChangesDateTime!=NEW.ChangesDateTime)
BEGIN
	-- Clear all sysprod database tables
	DELETE FROM ProductItemTree;
	DELETE FROM ProductItemLeaf;
	DELETE FROM ProductPrice;

	-- BaseProductTree
	INSERT INTO BaseProductTree(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		CAST(Product.ProductCode AS VARCHAR(50)) AS ItemId,
		Product.ProductCode AS ProductCode,
		0 AS IsClass,
		ProductPart.PartCode AS PartCode,
		0 AS RecursionLevel,
		0 AS MenuItem
	FROM Product
	JOIN ProductKernelParams ppkp ON ppkp.ProductCode = Product.ProductCode
	LEFT JOIN ProductPart ON ProductPart.ProductCode = Product.ProductCode
	LEFT JOIN ProductKernelParams ON ProductKernelParams.ProductCode = ProductPart.PartCode
	WHERE Product.ProductCode NOT IN (SELECT ClassCode FROM ProductClassification)
	  AND (ProductKernelParams.SysProdExplosionActive IS NULL OR ProductKernelParams.SysProdExplosionActive = 1 OR (ProductKernelParams.SysProdExplosionActive = 0 AND COALESCE(ProductPart.DefaultQty,0)>0))
	UNION ALL
	SELECT
		CAST(ProductClassification.ClassCode AS VARCHAR(50)) AS ItemId,
		Product.ProductCode AS ProductCode,
		1 AS IsClass,
		ProductClassification.ProductCode AS PartCode,
		0 AS RecursionLevel,
		CASE WHEN ppkp.ProductType=3 THEN 1 ELSE 0 END MenuItem
	FROM ProductClassification
	JOIN Product ON Product.ProductCode = ProductClassification.ClassCode
	JOIN ProductKernelParams ppkp ON ppkp.ProductCode = Product.ProductCode
	LEFT JOIN ProductPart ON ProductPart.ProductCode=ProductClassification.ClassCode AND ProductPart.PartCode=ProductClassification.ProductCode
	LEFT JOIN ProductKernelParams ON ProductKernelParams.ProductCode = ProductPart.PartCode
	WHERE (ProductKernelParams.SysProdExplosionActive IS NULL OR ProductKernelParams.SysProdExplosionActive = 1);
	
	-- Level 0
	INSERT INTO BaseProductTree_Level0(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem FROM BaseProductTree WHERE MenuItem=1;

	-- Level 1
	INSERT INTO BaseProductTree_Level1(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		Product.ItemId || '.' || Part.ItemId AS ItemId,
		Part.ProductCode AS ProductCode,
		Part.IsClass AS IsClass,
		Part.PartCode AS PartCode,
		Product.RecursionLevel + 1 AS RecursionLevel,
		Part.MenuItem AS MenuItem
	FROM BaseProductTree_Level0 AS Product
	JOIN BaseProductTree AS Part
	ON Product.PartCode = Part.ProductCode;

	-- Level 2
	INSERT INTO BaseProductTree_Level2(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		Product.ItemId || '.' || Part.ItemId AS ItemId,
		Part.ProductCode AS ProductCode,
		Part.IsClass AS IsClass,
		Part.PartCode AS PartCode,
		Product.RecursionLevel + 1 AS RecursionLevel,
		Part.MenuItem AS MenuItem
	FROM BaseProductTree_Level1 AS Product
	JOIN BaseProductTree AS Part ON Product.PartCode = Part.ProductCode
	WHERE Part.PartCode IS NOT NULL;

	-- Level 3
	INSERT INTO BaseProductTree_Level3(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		Product.ItemId || '.' || Part.ItemId AS ItemId,
		Part.ProductCode AS ProductCode,
		Part.IsClass AS IsClass,
		Part.PartCode AS PartCode,
		Product.RecursionLevel + 1 AS RecursionLevel,
		Part.MenuItem AS MenuItem
	FROM BaseProductTree_Level2 AS Product
	JOIN BaseProductTree AS Part ON Product.PartCode = Part.ProductCode
	WHERE Part.PartCode IS NOT NULL;

	-- Level 4
	INSERT INTO BaseProductTree_Level4(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		Product.ItemId || '.' || Part.ItemId AS ItemId,
		Part.ProductCode AS ProductCode,
		Part.IsClass AS IsClass,
		Part.PartCode AS PartCode,
		Product.RecursionLevel + 1 AS RecursionLevel,
		Part.MenuItem AS MenuItem
	FROM BaseProductTree_Level3 AS Product
	JOIN BaseProductTree AS Part ON Product.PartCode = Part.ProductCode
	WHERE Part.PartCode IS NOT NULL;

	-- Level 5
	INSERT INTO BaseProductTree_Level5(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		Product.ItemId || '.' || Part.ItemId AS ItemId,
		Part.ProductCode AS ProductCode,
		Part.IsClass AS IsClass,
		Part.PartCode AS PartCode,
		Product.RecursionLevel + 1 AS RecursionLevel,
		Part.MenuItem AS MenuItem
	FROM BaseProductTree_Level4 AS Product
	JOIN BaseProductTree AS Part ON Product.PartCode = Part.ProductCode
	WHERE Part.PartCode IS NOT NULL;

	-- Level 6
	INSERT INTO BaseProductTree_Level6(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		Product.ItemId || '.' || Part.ItemId AS ItemId,
		Part.ProductCode AS ProductCode,
		Part.IsClass AS IsClass,
		Part.PartCode AS PartCode,
		Product.RecursionLevel + 1 AS RecursionLevel,
		Part.MenuItem AS MenuItem
	FROM BaseProductTree_Level5 AS Product
	JOIN BaseProductTree AS Part ON Product.PartCode = Part.ProductCode
	WHERE Part.PartCode IS NOT NULL;

	-- Level 7
	INSERT INTO BaseProductTree_Level7(ItemId, ProductCode, IsClass, PartCode, RecursionLevel, MenuItem)
	SELECT
		Product.ItemId || '.' || Part.ItemId AS ItemId,
		Part.ProductCode AS ProductCode,
		Part.IsClass AS IsClass,
		Part.PartCode AS PartCode,
		Product.RecursionLevel + 1 AS RecursionLevel,
		Part.MenuItem AS MenuItem
	FROM BaseProductTree_Level6 AS Product
	JOIN BaseProductTree AS Part ON Product.PartCode = Part.ProductCode
	WHERE Part.PartCode IS NOT NULL;

	-- Produce ProductItemTree table
	INSERT INTO ProductItemTree(ItemId, Context, ProductCode, IsClass, RecursionLevel)
	SELECT ItemId, Context, ProductCode, IsClass, RecursionLevel
	FROM (
		SELECT
			PI.ItemId AS ItemId,
			NULLIF(
				CASE
				   WHEN LENGTH(PI.ItemId) > LENGTH(CAST(PI.ProductCode AS VARCHAR(50)))
				   THEN SUBSTR(PI.ItemId, 1, LENGTH(PI.ItemId)-LENGTH('.' || CAST(PI.ProductCode AS VARCHAR(50))))
				   ELSE NULL
				END,
				''
			) AS Context,
			PI.ProductCode AS ProductCode,
			PI.IsClass AS IsClass,
			PI.RecursionLevel AS RecursionLevel
		FROM 
			ProductTreeView PI
		GROUP BY PI.ItemId, PI.ProductCode
	) T
	WHERE Context IS NOT NULL;
	
	-- Produce ProductItemLeaf table
	INSERT INTO ProductItemLeaf(ProductCode, PartCode, MinQty, MaxQty, DefaultQty, PartType)
	SELECT B.ProductCode, B.PartCode, A.MinQty, A.MaxQty, A.DefaultQty, A.PartType
	FROM (
		SELECT ProductCode, PartCode 
		FROM ProductTreeView
		GROUP BY ProductCode, PartCode
	) B 
	LEFT JOIN ProductPart A ON B.ProductCode=A.ProductCode AND B.PartCode=A.PartCode
	WHERE B.PartCode IS NOT NULL;

	-- ProductPrice
	INSERT INTO ProductPrice(ItemId,Context,ProductCode,IsClass,MenuItem,PriceKey,Source,PriceListId,ValidFrom,ValidThru)
	SELECT
		Product.ItemId      AS ItemId,
		Price.Context       AS Context,
		Price.ProductCode   AS ProductCode,
		Product.IsClass     AS IsClass,
		1                   AS MenuItem,
		Price.PriceKey      AS PriceKey,
		1                   AS Source,
		Price.PriceListId   AS PriceListId,
		Price.ValidFrom     AS ValidFrom,
		Price.ValidThru     AS ValidThru
	FROM (
		SELECT 
			ItemId, 
			Context, 
			ProductCode, 
			IsClass, 
			0 AS RecursionLevel
		FROM ProductItemTree
		WHERE RecursionLevel=1
		UNION ALL
		SELECT 
			PIT.Itemid||'.'||COALESCE(PIL.PartCode,PIT.ProductCode) AS ItemId, 
			PIT.Itemid AS Context, 
			COALESCE(PIL.PartCode,PIT.ProductCode) AS ProductCode, 
			PIT.IsClass, 
			PIT.RecursionLevel
		FROM ProductItemTree PIT
		LEFT JOIN ProductItemLeaf PIL ON PIL.ProductCode=PIT.ProductCode
	) Product
	JOIN Price
	  ON Price.ProductCode=Product.ProductCode AND (
			SUBSTR(
				REPLACE(
					Product.ItemId,
					CASE WHEN COALESCE(TRIM(Price.Context),'') = ''
						THEN ''
						ELSE '.' || Price.Context || '.'
					END || CAST(Price.ProductCode AS VARCHAR(50)),
					'*'
				),
				-1
			)='*'
		OR
			Product.ItemId = (
				CASE WHEN COALESCE(TRIM(Price.Context),'') = ''
					THEN ''
					ELSE Price.Context || '.'
				END || CAST(Price.ProductCode AS VARCHAR(50))
			)
		);

	-- update the ProductCatalogChanges table
	UPDATE ProductCatalogChanges SET SchemaRevision=NEW.SchemaRevision, ChangesCounter=NEW.ChangesCounter, ChangesDateTime=NEW.ChangesDateTime;
END;

-- Updates the CheckCatalogChanges table with the
-- Product Catalog current states and triggers the
-- update if needed.
UPDATE temp.CheckCatalogChanges SET
	SchemaRevision=(SELECT MAX(Revision) FROM productdb.schema_version),
	ChangesCounter=(SELECT MAX(ChangesCount) FROM productdb.ProductCatalogChangesCounter),
	ChangesDateTime=(SELECT MAX(ChangesDateTime) FROM productdb.ProductCatalogChangesCounter);

-- Drop the temporary objects of this DDL script switch will never be used.
DROP TRIGGER TriggerCheckCatalogChanges;
DROP TABLE CheckCatalogChanges;
DROP TABLE BaseProductTree;
DROP TABLE BaseProductTree_level0; 
DROP TABLE BaseProductTree_level1; 
DROP TABLE BaseProductTree_level2; 
DROP TABLE BaseProductTree_level3; 
DROP TABLE BaseProductTree_level4; 
DROP TABLE BaseProductTree_level5; 
DROP TABLE BaseProductTree_level6; 
DROP TABLE BaseProductTree_level7; 
DROP VIEW ProductTreeView;
