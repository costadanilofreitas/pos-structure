-- noinspection SqlNoDataSourceInspectionForFile

-- Schema: users
-- Brief: Control user access into POS
-- Created by: amerolli
-- Table schema_version: must be defined for database update through the Persistence Component

CREATE TABLE schema_version AS
SELECT "$Author: rrosauro $" AS Author,
       "$Date: 2009-11-27 11:37:18 -0200 (Fri, 27 Nov 2009) $" AS LastModifiedAt,
       "$Revision: 639c4e25b8f4275fcf66c5a51c2ab9b00cb137d7$" AS Revision;

-- Table Users:
--   This table keeps basic user information for identification and authentication 
--   purposes.
--   +------------------+--------------------------------------+-----+------+---------+
--   | Field Name       | Field description                    | Key | NULL | Default |
--   +------------------+--------------------------------------+-----+------+---------+
--   | UserId           | The user unique identification, used |  P  |  No  |   N/D   |
--   |                  | for numeric login.                   |     |  No  |   N/D   |
--   | UserName         | Unique user name to be used in       |     |  No  |   N/D   |
--   |                  | alternate login procedure.           |     |  No  |   N/D   |
--   | LongName         | Complete name of user.               |     |  No  |   N/D   |
--   | Password         | HMAC digest of password (key) and    |     |  No  |   N/D   |
--   |                  | username (message).                  |     |  No  |   N/D   |
--   | PasswordValidity | Date limit to current password; if   |     | Yes  |   N/D   |
--   |                  | null there is no limit.              |     |  No  |   N/D   |
--   | Level            | User Security Level                  |     |  No  |   0     |
--   | Status           | 0->active, 1->inactive,              |     |  No  |   N/D   |
--   |                  | 2->licensed, 3->vacation,            |     |  No  |   N/D   |
--   |                  | 99->terminated                       |     |  No  |   N/D   |
--   | AdmissionDate    | Admission date                       |     |  No  |   N/D   |
--   | TerminationDate  | Termination date                     |     | Yes  |   N/D   |
--   | PayRate          | Pay rate                             |     | Yes  |   N/D   |
--   +------------------+--------------------------------------+-----+------+---------+
CREATE TABLE Users (
	UserId				    INTEGER	PRIMARY KEY AUTOINCREMENT,
	UserName			    VARCHAR(15) NOT NULL,
	LongName			    VARCHAR(50) NOT NULL,
	Password			    VARCHAR(32) NOT NULL,
	PasswordValidity	DATETIME,
	Level            INTEGER NOT NULL DEFAULT 0,
	Status	           INTEGER NOT NULL,
	AdmissionDate    DATE NOT NULL,
	TerminationDate  DATETIME,
	PayRate          VARCHAR(30),
	BadgeNumber      TEXT,
	FingerPrintMinutiae BLOB
);

-- Table Shift:
--   This table describes all possible shifts combinations.
--   +------------------+--------------------------------------+-----+------+---------+
--   | Field Name       | Field description                    | Key | NULL | Default |
--   +------------------+--------------------------------------+-----+------+---------+
--   | ShiftId          | Shift unique identification.         |  P  |  No  |   N/D   |
--   | Name             | Description.                         |     |  No  |   N/D   |
--   | WorkDays         | Indicates the workdays starting at   |     |  No  | 0111110 |
--   |                  | monday.                              |     |  No  |         |
--   | StartTime        | Shift start time.                    |     |  No  | 08:00   |
--   | EndTime          | Shift end time.                      |     |  No  | 18:00   |
--   | NumBreaks        | Number of allowed breaks.            |     |  No  |    1    |
--   | BreakDuration    | Time in minutes for each break.      |     |  No  |   60    |
--   +------------------+--------------------------------------+-----+------+---------+
CREATE TABLE Shift (
	ShiftId				INTEGER NOT NULL,
	Name				VARCHAR(20),
	WorkDays			INTEGER NOT NULL DEFAULT 62, -- '0111110'
	StartTime			VARCHAR(5) NOT NULL DEFAULT '08:00',
	EndTime				VARCHAR(5) NOT NULL DEFAULT '18:00',
	
	-- TODO: create a break table (we may have different break times into the same shift)
	
	NumBreaks			INTEGER	NOT NULL DEFAULT 1,
	BreakDuration		INTEGER NOT NULL DEFAULT 60,
	PRIMARY KEY(ShiftId)
);

-- Table Allocation:
--   This table allocates employees to shifts.
--   +------------------+--------------------------------------+-----+------+---------+
--   | Field Name       | Field description                    | Key | NULL | Default |
--   +------------------+--------------------------------------+-----+------+---------+
--   | Id               | Shift/User relation unique id (auto).|  P  |  No  |   N/D   |
--   | ShiftId          | Shift unique identification.         |     |  No  |   N/D   |
--   | UserId           | The user unique identification.      |     |  No  |   N/D   |
--   | ShiftTolerance   | Time in minutes of tolerance.        |     |  No  |    0    |
--   +------------------+--------------------------------------+-----+------+---------+
CREATE TABLE Allocation (
	Id					INTEGER PRIMARY KEY AUTOINCREMENT,
	ShiftId				INTEGER NOT NULL,
	UserId				INTEGER NOT NULL,
	ShiftTolerance		INTEGER NOT NULL DEFAULT 0
);


--
-- Default user (1/1)
--
INSERT INTO Users(UserId, UserName, LongName, Password, Level, Status, AdmissionDate) VALUES(6626, 'Suporte', 'Suporte', '2a68fba8d921e4bd3e5b03ba401bf6eb', 30, 0, '2019-01-01');
INSERT INTO Users(UserId, UserName, LongName, Password, Level, Status, AdmissionDate) VALUES(31415, 'Delivery', 'Delivery', '7c3d32402e4509c78b5c4ed6552ef756', 21, 0, '2019-01-01');
INSERT INTO Users(UserId, UserName, LongName, Password, Level, Status, AdmissionDate) VALUES(2718, 'Totem', 'Totem', 'b1eac4329ffd24ef085940fe70904e00', 21, 0, '2019-01-01');
