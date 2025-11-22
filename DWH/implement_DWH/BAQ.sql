USE CRH_DWH;
GO

/* WARNING: THIS SCRIPT DELETES ALL TABLES! YOU WILL LOSE ALL DATA */

drop table if exists
    FactQuestionBAQ

GO
-------------------------- FACTS TABLE -------------------------- 

-- FactQuestionBAQ

CREATE TABLE FactQuestionBAQ (
	QuestionKey INT PRIMARY KEY,
	TestKey INT,
	NormItemID INT,
	Norm1 INT,
	Norm2 INT,
	Norm3 INT,
	Norm4 INT,
	Norm5 INT,
	IpsItemID INT,
	Ips1 INT,
	Ips2 INT,
	Ips3 INT,
	Ips4 INT,
	Ips5 INT,
	AnomaliesKey INT
);
GO

-------------------------- KEYS -------------------------- 

ALTER TABLE FactQuestionBAQ
ADD  
FOREIGN KEY (TestKey) REFERENCES FactTest(TestKey),
FOREIGN KEY (AnomaliesKey) REFERENCES DimQuestionAnomalies(AnomaliesKey)
GO