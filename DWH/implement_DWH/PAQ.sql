
USE CRH_DWH
GO

/* WARNING: THIS SCRIPT DELETES ALL TABLES! YOU WILL LOSE ALL DATA */

drop table if exists
    FactQuestionPAQ
GO
-------------------------- FACTS TABLE -------------------------- 

-- FactQuestionPAQ

create table FactQuestionPAQ (
	QuestionKey int primary key,
    TestKey int,
	AnomaliesKey int,
    LeftStatement varchar(8),
    RightStatement varchar(8),
    AnswerVal int
);
GO

-------------------------- KEYS -------------------------- 

ALTER TABLE FactQuestionPAQ
ADD  
FOREIGN KEY (TestKey) REFERENCES FactTest(TestKey),
FOREIGN KEY (AnomaliesKey) REFERENCES DimQuestionAnomalies(AnomaliesKey)
GO
