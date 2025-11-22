USE CRH_DWH;
GO

/* WARNING: THIS SCRIPT DELETES ALL TABLES! YOU WILL LOSE ALL DATA */

drop table if exists
    FactQuestionSJT

GO
-------------------------- FACTS TABLE -------------------------- 

create table FactQuestionSJT (
	QuestionKey int primary key,
    TestKey int,
	AnomaliesKey int,
    ItemID int,
    AnswerSequence1 int,
    AnswerSequence2 int,
    AnswerSequence3 int,
    TimeSpent float,
);
GO

-------------------------- KEYS -------------------------- 

ALTER TABLE FactQuestionSJT
ADD  
FOREIGN KEY (TestKey) REFERENCES FactTest(TestKey),
FOREIGN KEY (AnomaliesKey) REFERENCES DimQuestionAnomalies(AnomaliesKey)
GO