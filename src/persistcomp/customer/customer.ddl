-- noinspection SqlNoDataSourceInspectionForFile

-- Schema: customer
-- Brief: Customer component controller
-- Created by: eribeiro
-- Table schema_version: must be defined for database update through the CustomerPersistence component

CREATE TABLE schema_version AS
SELECT "$Author: eribeiro $" AS Author,
       "$Date: 2020-12-18 15:00:00 -0300$" AS LastModifiedAt,
       "$Revision: 69a663b99f2281301896fda1599d57996fb4e763$" AS Revision;

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CREATE TABLE Customer (
  Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  Phone VARCHAR,
  Document VARCHAR,
  Name VARCHAR,
  AddressId INTEGER NOT NULL
);

CREATE UNIQUE INDEX 'idx_Phone_Id' ON 'Customer' ('Phone');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CREATE TABLE CustomerAddress (
  Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  ZipCode VARCHAR,
  City VARCHAR,
  Street VARCHAR,
  Neighborhood VARCHAR,
  Number VARCHAR,
  Complement VARCHAR,
  ReferencePoint VARCHAR
  
);

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
