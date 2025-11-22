USE CRH_DWH;
GO

/* WARNING: THIS SCRIPT DELETES ALL TABLES! YOU WILL LOSE ALL DATA */

drop table if exists
    FactQuestionMDQ
GO
-------------------------- FACTS TABLE -------------------------- 

-- FactQuestionMDQ

CREATE TABLE FactQuestionMDQ (
	QuestionKey INT PRIMARY KEY,
	TestKey INT NOT NULL,
	ItemID INT,
	FirstVal INT,
	SecondVal INT,
	ThirdVal INT,
	FourthVal INT,
	FifthVal INT,
	SixthVal INT,
	AnomaliesKey INT
);
GO

-------------------------- KEYS -------------------------- 

ALTER TABLE FactQuestionMDQ
ADD  
FOREIGN KEY (TestKey) REFERENCES FactTest(TestKey),
FOREIGN KEY (AnomaliesKey) REFERENCES DimQuestionAnomalies(AnomaliesKey)
GO