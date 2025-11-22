/* WARNING: THIS SCRIPT DELETES ALL TABLES! YOU WILL LOSE ALL DATA */

drop table if exists
    FactQuestionFCA, 
    FactQuestionSJT,
    FactQuestionBAQ,
    FactQuestionPAQ,
    FactQuestionMDQ,
    FactTest,
    DimCandidate,
	DimCompetence,
	DimTestAnomalies,
    DimQuestionAnomalies,
	DimDate,
	DimTime
GO

-------------------------- DIMENSION TABLES -------------------------- 

-- DimDate

CREATE TABLE DimDate (
    DateKey INT PRIMARY KEY,
    Date DATE NOT NULL,
    Year INT NOT NULL,
    Month INT NOT NULL,
    Day INT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    DayOfWeek INT NOT NULL,
    DayOfWeekName VARCHAR(20) NOT NULL,
    IsWeekend BIT NOT NULL
);
GO

----  Voeg datums toe die tussen de start en eindtijd vallen
BEGIN
    DECLARE @StartDate DATE = '2007-01-01';
    DECLARE @EndDate DATE = '2024-12-31';
    DECLARE @BatchSize INT = 1000;
    DECLARE @CurrentBatch INT = 0;

    WHILE @StartDate <= @EndDate
    BEGIN
        INSERT INTO DimDate (DateKey, Date, Year, Month, Day, MonthName, DayOfWeek, DayOfWeekName, IsWeekend)
        SELECT 
            CAST(CONVERT(VARCHAR(8), DATEADD(DAY, number, @StartDate), 112) AS INT),
            DATEADD(DAY, number, @StartDate),
            YEAR(DATEADD(DAY, number, @StartDate)),
            MONTH(DATEADD(DAY, number, @StartDate)),
            DAY(DATEADD(DAY, number, @StartDate)),
            DATENAME(MONTH, DATEADD(DAY, number, @StartDate)),
            DATEPART(WEEKDAY, DATEADD(DAY, number, @StartDate)),
            DATENAME(WEEKDAY, DATEADD(DAY, number, @StartDate)),
            CASE WHEN DATEPART(WEEKDAY, DATEADD(DAY, number, @StartDate)) IN (1, 7) THEN 1 ELSE 0 END
        FROM master.dbo.spt_values 
        WHERE type = 'P' 
        AND number < @BatchSize 
        AND DATEADD(DAY, number, @StartDate) <= @EndDate;

        SET @StartDate = DATEADD(DAY, @BatchSize, @StartDate);
        SET @CurrentBatch = @CurrentBatch + 1;
        
        PRINT 'Processed batch ' + CAST(@CurrentBatch AS VARCHAR(10));
    END;
END;


-- select count(*) from DimDate;

-- DimTime 

CREATE TABLE DimTime (
    TimeKey INT PRIMARY KEY,
    uren INT,
    minuten INT,
    seconden INT,
    uur_12_not INT,
	tekst TIME,
    am_pm CHAR(2),
);
GO
 
BEGIN
    WITH Numbers AS (
        SELECT TOP (86400) -- 24*60*60 seconds in a day
            ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS N
        FROM master.dbo.spt_values a
        CROSS JOIN master.dbo.spt_values b
    )
    INSERT INTO DimTime (TimeKey, uren, minuten, seconden, am_pm, tekst)
    SELECT 
        (N / 3600) * 10000 + ((N % 3600) / 60) * 100 + (N % 60) AS TimeKey,
        (N / 3600) AS uren,
        (N % 3600) / 60 AS minuten,
        N % 60 AS seconden,
        CASE WHEN (N / 3600) < 12 THEN 'AM' ELSE 'PM' END AS am_pm,
        CONCAT(
            RIGHT('0' + CAST((N / 3600) AS VARCHAR(2)), 2), ':', 
            RIGHT('0' + CAST(((N % 3600) / 60) AS VARCHAR(2)), 2), ':', 
            RIGHT('0' + CAST((N % 60) AS VARCHAR(2)), 2)
        ) AS tekst
    FROM Numbers;
END

-- select count(*) from DimTime;

-- DimCandidate

create table DimCandidate (
	CandidateKey int primary key, 
    ID int, 
    InstanceID int, 
	Organisation varchar(100), 
    ChosenLanguage varchar(100),
    ChosenGender varchar(50),
    Gender varchar(50),
    Qualification varchar(50)
);
GO

-- DimTestAnomalies
create table DimTestAnomalies (
	AnomaliesKey int primary key,
    SameAnswer float,
    TooFast bit, 
    TooSlow bit,
	DBSCAN bit,
	Neighbours bit,
    Copod bit,
    Ecod bit,
    iForest bit,
    Lof bit,
    Abod bit,
    PyodEnsemble bit,
    AnomalyScore float,
	IsAnomaly bit
);
GO

-- DimQuestionAnomalies
create table DimQuestionAnomalies (
	AnomaliesKey int primary key,
	SameAnswer bit,
	TooFast bit,
	TooSlow bit
);
GO

-------------------------- FACTS TABLE -------------------------- 

-- FactTest

create table FactTest (
	TestKey int primary key,
	Test varchar(10),
    CandidateKey int,
	CreatedDateKey int, 
    ModifiedDateKey int,
    PostedDateKey int,
    TestStartTimeKey int,
    TestFinishTimeKey int,
    AnomaliesKey int,
    VersionNumber varchar(10),
	TimeSpent int
);
GO

-------------------------- KEYS -------------------------- 

ALTER TABLE FactTest
ADD  
FOREIGN KEY (CreatedDateKey) REFERENCES DimDate(DateKey),
FOREIGN KEY (ModifiedDateKey) REFERENCES DimDate(DateKey),
FOREIGN KEY (PostedDateKey) REFERENCES DimDate(DateKey),
FOREIGN KEY (TestStartTimeKey) REFERENCES DimTime(TimeKey),
FOREIGN KEY (TestFinishTimeKey) REFERENCES DimTime(TimeKey),
FOREIGN KEY (CandidateKey) REFERENCES DimCandidate(CandidateKey),
FOREIGN KEY (AnomaliesKey) REFERENCES DimTestAnomalies(AnomaliesKey)
GO
