USE CRH_DWH;
GO

/* WARNING: THIS SCRIPT DELETES ALL TABLES! YOU WILL LOSE ALL DATA */

drop table if exists
    FactQuestionFCA, 
    DimCompetence


GO
-------------------------- DIMENSIONS TABLE -------------------------- 

-- DimCompetence
create table DimCompetence (
	CompetenceKey int primary key, 
	CompetenceCode int,
    ItemID int,
    IdealAnswerSequence1 int, 
    IdealAnswerSequence2 int, 
    IdealAnswerSequence3 int
);
GO

-------------------------- FACTS TABLE -------------------------- 

-- FactQuestionFCA
create table FactQuestionFCA (
	QuestionKey int primary key,
    TestKey int,
    Competence1Key int,
    Competence2Key int,
    Competence3Key int,
    Competence4Key int,
	AnomaliesKey int,
    ItemID int,
    AnswerSequence1 int,
    AnswerSequence2 int,
    AnswerSequence3 int,
    TimeSpent float,
);
GO

-------------------------- KEYS -------------------------- 

ALTER TABLE FactQuestionFCA 
ADD  
FOREIGN KEY (TestKey) REFERENCES FactTest(TestKey),
FOREIGN KEY (Competence1Key) REFERENCES DimCompetence(CompetenceKey),
FOREIGN KEY (Competence2Key) REFERENCES DimCompetence(CompetenceKey),
FOREIGN KEY (Competence3Key) REFERENCES DimCompetence(CompetenceKey),
FOREIGN KEY (Competence4Key) REFERENCES DimCompetence(CompetenceKey),
FOREIGN KEY (AnomaliesKey) REFERENCES DimQuestionAnomalies(AnomaliesKey)
GO