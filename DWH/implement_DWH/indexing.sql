-----------------------------
-- get question with anomaly
-----------------------------

-- FCA

CREATE VIEW dbo.AnomQuestFCA_view
WITH SCHEMABINDING
AS
select q.AnomaliesKey AS AnomaliesKey, SameAnswer, TooFast, TooSlow, QuestionKey, TestKey, Competence1Key, Competence2Key, Competence3Key, Competence4Key, ItemID, AnswerSequence1, AnswerSequence2, AnswerSequence3, TimeSpent
from dbo.DimQuestionAnomalies qa 
inner join dbo.FactQuestionFCA q on q.AnomaliesKey = qa.AnomaliesKey;
GO

CREATE UNIQUE CLUSTERED INDEX FCAView_pk on AnomQuestFCA_view(AnomaliesKey, QuestionKey, TestKey);
GO

CREATE INDEX fca_non_clustered ON AnomQuestFCA_view(AnomaliesKey) INCLUDE (SameAnswer, TooFast, TooSlow, QuestionKey, TestKey, Competence1Key, Competence2Key, Competence3Key, Competence4Key, ItemID, AnswerSequence1, AnswerSequence2, AnswerSequence3, TimeSpent);
GO

-- SJT
CREATE VIEW dbo.AnomQuestSJT_view
WITH SCHEMABINDING
AS
select q.AnomaliesKey AS AnomaliesKey, SameAnswer, TooFast, TooSlow, QuestionKey, TestKey, ItemID, AnswerSequence1, AnswerSequence2, AnswerSequence3, TimeSpent
from dbo.DimQuestionAnomalies qa 
inner join dbo.FactQuestionSJT q on q.AnomaliesKey = qa.AnomaliesKey;
GO

CREATE UNIQUE CLUSTERED INDEX SJTView_pk on AnomQuestSJT_view(AnomaliesKey, QuestionKey, TestKey);
GO

CREATE INDEX sjt_non_clustered ON AnomQuestSJT_view(AnomaliesKey) INCLUDE (SameAnswer, TooFast, TooSlow, QuestionKey, TestKey, ItemID, AnswerSequence1, AnswerSequence2, AnswerSequence3, TimeSpent)
GO

-------------------------
-- get general test data
-------------------------

CREATE INDEX fk_test_idx ON FactTest(CandidateKey, AnomaliesKey, CreatedDateKey) INCLUDE(TestKey, Test, TimeSpent)
GO

CREATE INDEX date_idx ON DimDate(DateKey, Date, Year)
GO
