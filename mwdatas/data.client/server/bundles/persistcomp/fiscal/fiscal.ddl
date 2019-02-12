-- Schema: fiscal
-- Brief: Fiscal database definition
-- Created by: garaujo
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author$" AS Author,
       "$Date$" AS LastModifiedAt,
       "$Revision: 135245c4a7dd2pq2b188a7125efa9c21eb2945399$" AS Revision;

CREATE TABLE FiscalData (
    PosId INTEGER NOT NULL,
    OrderId INTEGER NOT NULL,
    XMLRequest VARCHAR NOT NULL,
    NumeroNota VARCHAR NOT NULL,
    NumeroSat VARCHAR NOT NULL,
    SentToBKOffice INTEGER NOT NULL DEFAULT 0,
    NextDateToSend VARCHAR DEFAULT NULL,
    SentToNfce INTEGER DEFAULT 0,
    SentToBKC INTEGER DEFAULT 0,
    NextDateToSendToBKC VARCHAR,
    OrderPicture VARCHAR NOT NULL DEFAULT '1',
    DataNota VARCHAR NOT NULL DEFAULT '1',
    XMLResponse VARCHAR DEFAULT NULL,
    PRIMARY KEY(OrderId)
);

CREATE INDEX 'send_bko' ON 'FiscalData' ('SentToBKOffice', 'SentToNfce');
CREATE INDEX 'send_bkc' ON 'FiscalData' ('SentToBKC', 'SentToNfce');

CREATE TABLE PaymentData (
    PosId INTEGER NOT NULL,
    OrderId INTEGER NOT NULL,
    TenderSeqId INTEGER NOT NULL,
    Type INTEGER NOT NULL,
    Amount DECIMAL NOT NULL,
    Change DECIMAL,
    AuthCode VARCHAR,
    IdAuth VARCHAR,
    CNPJAuth VARCHAR,
    Bandeira INTEGER,
    ReceiptMerchant VARCHAR,
    ReceiptCustomer VARCHAR,
    PaymentId VARCHAR,
    ResponseFiscalId VARCHAR,
    PRIMARY KEY(OrderId,TenderSeqId)
);

CREATE TABLE FitaDetalhe (
    PosId INTEGER NOT NULL,
    BusinessPeriod VARCHAR NOT NULL,
    CloseTime DATETIME NOT NULL,
    SentToBKOffice INTEGER DEFAULT 0,
    PRIMARY KEY(PosId, BusinessPeriod)
);

CREATE TABLE BandeiraCartao (
    Bandeira INTEGER NOT NULL,
    Descricao VARCHAR,
    Type INTEGER NOT NULL,
    BKC_Id INTEGER,
    BKC_Nome VARCHAR,
    Detalhes VARCHAR,
    PRIMARY KEY(Bandeira)
);

-- Credito 1 | Voucher/Debito 2
INSERT INTO BandeiraCartao VALUES (1,'VISA',1,7766,'VISA','Credito');
INSERT INTO BandeiraCartao VALUES (10001,'Ticket',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20001,'Maestro',2,7798,'Maestro','Debito');
INSERT INTO BandeiraCartao VALUES (2,'MASTERCARD',2,7737,'Master Card','Credito');
INSERT INTO BandeiraCartao VALUES (10002,'Visa Vale',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20002,'Visa Electron',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (3,'DINERS',1,7770,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10003,'Sodexo',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20003,'Cabal',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (4,'AMERICAN EXPRESS',1,7769,'AMEX','Credito');
INSERT INTO BandeiraCartao VALUES (10004,'Nutricash',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (5,'SOLLO',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10005,'Greencard',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (6,'SIDECARD (REDECARD)',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10006,'Planvale',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (7,'PRIVATE LABEL (REDECARD)',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10007,'Banquet',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20007,'Private Label',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (8,'REDESHOP',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10008,'Verocheque',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (9,'Pão de Açucar',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10009,'Sapore',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10,'FININVEST (VISANET)',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10010,'BNB Clube',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (11,'JCB',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10011,'Valecard',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (12,'HIPERCARD',1,7798,'Other Cards', 'Credito');
INSERT INTO BandeiraCartao VALUES (10012,'Cabal',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20012,'Cabal',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (13,'AURA',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10013,'Elo',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20013,'Elo',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (14,'LOSANGO',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10014,'Discovery',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (15,'SOROCRED',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10015,'Goodcard',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10016,'Policard',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10017,'Cardsystem',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10018,'Bonus CBA',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10019,'Alelo',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10020,'Banescard',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (21,'BANRISUL',2,7798,'Other Cards','');
INSERT INTO BandeiraCartao VALUES (10021,'Alelo',2,7798,'Other Cards','Refeicao');
INSERT INTO BandeiraCartao VALUES (10022,'Alelo',2,7798,'Other Cards','Alimentacao');
INSERT INTO BandeiraCartao VALUES (10023,'Alelo',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (10024,'Ticket',2,7798,'Other Cards','Refeicao');
INSERT INTO BandeiraCartao VALUES (10025,'Ticket',2,7798,'Other Cards','Alimentacao');
INSERT INTO BandeiraCartao VALUES (10026,'Ticket',2,7798,'Other Cards','Parceiro');
INSERT INTO BandeiraCartao VALUES (10027,'Ticket',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (10028,'Sodexo',2,7798,'Other Cards','Refeicao');
INSERT INTO BandeiraCartao VALUES (10029,'Sodexo',2,7798,'Other Cards','Alimentacao');
INSERT INTO BandeiraCartao VALUES (10030,'Sodexo',2,7798,'Other Cards','Gift');
INSERT INTO BandeiraCartao VALUES (10031,'Sodexo',2,7798,'Other Cards','Premium');
INSERT INTO BandeiraCartao VALUES (10032,'Sodexo',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (10033,'Sodexo',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (10051,'Planvale',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (10053,'Nutricash',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (10054,'Ticket',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (10055,'Valecard',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (30,'Cabal',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (31,'Elo',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (20032,'Elo',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (33,'Policard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (20034,'Policard',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (35,'Banescard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (20036,'Banescard',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (10037,'Sorocred',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20037,'Hipercard',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (38,'Cetelem',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10039,'Valemulti',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10040,'Valefrota',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (41,'Sicredi',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (20042,'Sicredi',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (43,'Coopercred',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10044,'Coopercred',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (45,'A Vista',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10046,'Valefácil',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10047,'VR',2,7798,'Other Cards','Refeicao');
INSERT INTO BandeiraCartao VALUES (10048,'VR',2,7798,'Other Cards','Alimentacao');
INSERT INTO BandeiraCartao VALUES (10049,'VR',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (10050,'VR',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (10052,'Banrisul',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (57,'Credisystem',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (58,'Banpará',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (20059,'Banpará',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (60,'Amazoncard',1,17798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (61,'Yamada',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (62,'Goiascard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (63,'Credpar',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (64,'Boticario',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (65,'Ascard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (66,'Jetpar',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (67,'Maxxcard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (68,'Garantido',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (69,'Amazon Prime',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (70,'CredZ',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10070,'VR Benefício',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (71,'Credishop',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10071,'Planvale',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (20071,'Sorocred',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (10072,'Planvale',2,7798,'Other Cards','Alimentacao');
INSERT INTO BandeiraCartao VALUES (20072,'Maxxicard',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (73,'Libercard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10073,'Planvale',2,7798,'Other Cards','Refeicao');
INSERT INTO BandeiraCartao VALUES (20073,'Maxxicard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10074,'Planvale',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (20074,'Maxxicard',2,7798,'Other Cards','Gift');
INSERT INTO BandeiraCartao VALUES (10075,'Planvale',2,7798,'Other Cards','Farmácia');
INSERT INTO BandeiraCartao VALUES (20075,'Maxxicard',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (10076,'Peela',2,7798,'Other Cards','Gift');
INSERT INTO BandeiraCartao VALUES (10077,'Libercard',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (78,'Peela',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10079,'Up',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (10080,'Up',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (10081,'Up',2,7798,'Other Cards','Cultura');
INSERT INTO BandeiraCartao VALUES (10082,'Elo',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (10083,'VR',2,7798,'Other Cards','Voucher');
INSERT INTO BandeiraCartao VALUES (82,'GETNET',0,7798,'Other Cards',''); -- type 0
INSERT INTO BandeiraCartao VALUES (84,'Banrisul',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (20085,'Banrisul',2,7798,'Other Cards','Debito');
INSERT INTO BandeiraCartao VALUES (86,'Verdecard',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (87,'Refeisul',1,7798,'Other Cards','Credito');
INSERT INTO BandeiraCartao VALUES (10088,'Refeisul',2,7798,'Other Cards','Combustivel');
INSERT INTO BandeiraCartao VALUES (10089,'Refeisul',2,7798,'Other Cards','Alimentacao');
INSERT INTO BandeiraCartao VALUES (125,'VISANET - ESPECIFICAÇÃO 4.1',0,7798,'Other Cards', ''); -- type 0
