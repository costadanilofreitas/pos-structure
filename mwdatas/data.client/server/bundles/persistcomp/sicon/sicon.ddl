-- Schema: siconUploade
-- Brief: Fiscal database definition
-- Created by: ealmeida
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: $" AS Revision;

CREATE TABLE SiconUploadHistory (
  Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  InitialOrderId INTEGER NOT NULL,
  FinalOrderId INTEGER NOT NULL,
  EventDate DATE NOT NULL,
  EventStatus VARCHAR NOT NULL,
  ErrorDescription VARCHAR
);

CREATE UNIQUE INDEX 'idx_SiconUploadHistory_FinalOrderId' ON 'SiconUploadHistory' ('FinalOrderId');

CREATE TABLE SiconPaymentInfo (
  Bandeira INTEGER NOT NULL PRIMARY KEY,
  Sicon_Id VARCHAR NOT NULL,
  Sicon_Nome VARCHAR NOT NULL
);

INSERT INTO SiconPaymentInfo VALUES (1,7766,'VISA');
INSERT INTO SiconPaymentInfo VALUES (10001,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20001,7798,'Maestro');
INSERT INTO SiconPaymentInfo VALUES (2,7737,'Master Card');
INSERT INTO SiconPaymentInfo VALUES (10002,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20002,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (3,7770,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10003,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20003,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (4,7769,'AMEX');
INSERT INTO SiconPaymentInfo VALUES (10004,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (5,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10005,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (6,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10006,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (7,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10007,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20007,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (8,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10008,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (9,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10009,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10010,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (11,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10011,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (12,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10012,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20012,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (13,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10013,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20013,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (14,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10014,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (15,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10015,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10016,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10017,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10018,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10019,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10020,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (21,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10021,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10022,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10023,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10024,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10025,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10026,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10027,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10028,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10029,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10030,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10031,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10032,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10033,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10051,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10053,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10054,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10055,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (30,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (31,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20032,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (33,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20034,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (35,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20036,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10037,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20037,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (38,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10039,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10040,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (41,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20042,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (43,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10044,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (45,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10046,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10047,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10048,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10049,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10050,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10052,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (57,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (58,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20059,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (60,17798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (61,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (62,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (63,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (64,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (65,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (66,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (67,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (68,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (69,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (70,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10070,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (71,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10071,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20071,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10072,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20072,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (73,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10073,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20073,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10074,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20074,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10075,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20075,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10076,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10077,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (78,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10079,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10080,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10081,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10082,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10083,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (82,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (84,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (20085,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (86,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (87,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10088,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (10089,7798,'Other Cards');
INSERT INTO SiconPaymentInfo VALUES (125,7798,'Other Cards');
