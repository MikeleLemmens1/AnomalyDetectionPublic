USE CRH_DWH
GO

----------------------------------
-- Change keys that have 0 to NULL
----------------------------------

UPDATE FactTest
SET AnomaliesKey = NULL
WHERE AnomaliesKey = 0;
GO

UPDATE FactQuestionFCA
SET AnomaliesKey = NULL
WHERE AnomaliesKey = 0;
GO

UPDATE FactQuestionSJT
SET AnomaliesKey = NULL
WHERE AnomaliesKey = 0;
GO

UPDATE FactQuestionFCA
SET Competence1Key = NULL
WHERE Competence1Key = 0;
GO

UPDATE FactQuestionFCA
SET Competence2Key = NULL
WHERE Competence2Key = 0;
GO

UPDATE FactQuestionFCA
SET Competence3Key = NULL
WHERE Competence3Key = 0;
GO

UPDATE FactQuestionFCA
SET Competence4Key = NULL
WHERE Competence4Key = 0;
GO

------------------------------------------------------------------
-- Remove rows with only 0 in Dim tables where added in dataframes
------------------------------------------------------------------

DELETE FROM DimCompetence
WHERE CompetenceKey = 0;
GO

DELETE FROM DimTestAnomalies
WHERE AnomaliesKey = 0;
GO

DELETE FROM DimQuestionAnomalies
WHERE AnomaliesKey = 0;
GO

------------------------------------
-- Calculate TimeSpent for FCA tests
------------------------------------

UPDATE FactTest
SET TimeSpent = (
    SELECT DATEDIFF(SECOND, CONVERT(DATETIME, st.tekst), 
        CASE 
            WHEN CONVERT(DATETIME, f.tekst) < CONVERT(DATETIME, st.tekst) 
            THEN DATEADD(DAY, 1, CONVERT(DATETIME, f.tekst)) 
            ELSE CONVERT(DATETIME, f.tekst) 
        END
    )
    FROM FactTest t
    INNER JOIN DimTime st ON t.TestStartTimeKey = st.TimeKey
    INNER JOIN DimTime f ON t.TestFinishTimeKey = f.TimeKey
    WHERE t.TestKey = FactTest.TestKey AND t.test = 'FCA'
);
GO

-----------------------------------------
-- Change the LanguageGUID in DimCandidate
-----------------------------------------

UPDATE DimCandidate
SET ChosenLanguage = 'en-INT'
WHERE ChosenLanguage = '65CAFEA9-CF49-43ED-99AA-83AFE0539978';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'nl-BE'
WHERE ChosenLanguage = 'FADAABC8-26DD-458B-B07E-BF96B4B3FCED';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'fr-BE'
WHERE ChosenLanguage = 'BE3C46AE-0192-4A9B-ACEE-37E51836F77C';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'en-GB'
WHERE ChosenLanguage = 'BE39F135-6EF5-47E0-92D9-81B13BF9BEAA';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'en-US'
WHERE ChosenLanguage = '11BBB1BC-0CCD-4C9B-B0BE-5EFF9E634F75';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'sv-SE'
WHERE ChosenLanguage = '84519898-A081-44B3-BBB6-CA26F2E87E78';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'es-ES'
WHERE ChosenLanguage = 'D1E16E4B-9820-4203-A6AF-85A0538578CE';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'no-NO'
WHERE ChosenLanguage = '4348786F-1E2C-450D-8153-7C1BF429FEED';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'ru-UA'
WHERE ChosenLanguage = 'B26EA97C-651B-4DDA-ABE1-63D1850D89AF';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'de-DE'
WHERE ChosenLanguage = '747648B9-6256-4FFB-8513-A46BB50B0573';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'hu-HU'
WHERE ChosenLanguage = '1471B8FD-F9AC-412A-86B7-2665BC75995C';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'pl-PL'
WHERE ChosenLanguage = 'A01BF890-698E-44A6-9C15-888D5AFB7749';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'it-IT'
WHERE ChosenLanguage = 'A80A08DB-5382-4025-B7B1-5AC73F2DA4CB';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'sk-SK'
WHERE ChosenLanguage = 'B960D5FA-1221-4898-89E4-0BB41975A064';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'nl-NL'
WHERE ChosenLanguage = '050A046B-226D-4F40-873B-799F1AFD72C7';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'fr-FR'
WHERE ChosenLanguage = '81B7735E-083D-4AB5-AA59-42E74744F602';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'en-IE'
WHERE ChosenLanguage = '0ABBD19D-D3FF-4B4A-A54A-CBF10F2B96D1';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'ro-RO'
WHERE ChosenLanguage = '51E23428-A55A-48E7-906C-B867799D5515';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'cs-CZ'
WHERE ChosenLanguage = '50334890-8BDC-4480-B3DF-5D824BC83C5C';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'da-DK'
WHERE ChosenLanguage = 'D472F838-82D5-4B44-98DA-A77918FCE979';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'fi-FI'
WHERE ChosenLanguage = '55D35DB7-A093-45C9-8BAA-7E1F88871D68';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'ru-RU'
WHERE ChosenLanguage = '1908113F-6F07-40FE-AE1B-4AC9F6F8E84A';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'en-AU'
WHERE ChosenLanguage = 'C3389FD0-E729-4D22-8024-B8D6C76C380D';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'bg-BG'
WHERE ChosenLanguage = '910E7451-CBFA-4156-BFFF-0549C3E841E4';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'uk-UA'
WHERE ChosenLanguage = '138E18CF-880E-4080-91C8-37090ED52B11';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'de-BE'
WHERE ChosenLanguage = '8E412238-4764-44A8-A3D4-4881415D971D';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'pt-PT'
WHERE ChosenLanguage = '9643C274-8B03-4825-A3FE-37A5AB7C1E42';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'tr-TR'
WHERE ChosenLanguage = 'B780D85C-3BDE-49AE-8EAB-3E9EC05A7A14';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'fr-LU'
WHERE ChosenLanguage = '7B568B41-B1BF-4FFA-BD30-58164515B012';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'de-CH'
WHERE ChosenLanguage = 'AE808929-AFD7-41CC-9811-DC00062C59FA';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'fr-CH'
WHERE ChosenLanguage = 'BF792B04-9D01-44BF-B29B-03F7B466EA3C';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'de-AT'
WHERE ChosenLanguage = 'C8CA719D-86B0-41FD-8F86-E822085616D7';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'zh-CN'
WHERE ChosenLanguage = 'F14929C3-8514-4567-B2CE-9B0FCCD5D078';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'el-GR'
WHERE ChosenLanguage = '947295A7-E1B7-4D33-874C-91329EFA3679';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'lt-LT'
WHERE ChosenLanguage = 'CFA5E625-D0BA-41DF-8257-2B8FD8E6FEB9';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'fr-INT'
WHERE ChosenLanguage = '41532D8C-28F4-4D84-B526-9F9B72EA4A23';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'en-SG'
WHERE ChosenLanguage = '1C723139-76B6-47E4-A8B1-84B7DFCE414D';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'ja-JP'
WHERE ChosenLanguage = '915B946B-95D3-4BC7-89D5-AB568D9BD947';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'ar-SA'
WHERE ChosenLanguage = '4B45700B-D100-4861-A3A5-9BF804C3D56E';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'pt-BR'
WHERE ChosenLanguage = 'DAA6B33F-893E-4DF6-A21E-D9170A5C3550';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'th-TH'
WHERE ChosenLanguage = 'B120C202-2D61-49C2-8300-6BD1B4E37276';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'en-CN'
WHERE ChosenLanguage = 'CAB407D8-06F9-41B2-9FF5-D6E940C54575';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'hr-HR'
WHERE ChosenLanguage = 'F524C40A-A307-4640-8B50-E9D7379BFA75';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'sr-CS'
WHERE ChosenLanguage = '5019D8D7-0E15-4D3B-A537-FA933C698E9D';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'es-LM'
WHERE ChosenLanguage = '681C91B5-D6C7-462A-AC6D-DC8B5ACD6471';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'zh-TW'
WHERE ChosenLanguage = '77CF2859-BFCD-4FB2-B1EF-E059A0594FEF';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'zh-HK'
WHERE ChosenLanguage = 'B6385003-C956-4D54-8FD2-53BBCAAC5FE8';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'en-BE'
WHERE ChosenLanguage = '2636BBE3-F44C-45FF-8970-DAB0D091042B';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'de-LU'
WHERE ChosenLanguage = '63B7DCBF-919E-49A6-8BF4-7CD9042C4C44';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'et-EE'
WHERE ChosenLanguage = '902D3847-8BD1-45B8-BB3E-9D5DA1088204';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'ga-IRL'
WHERE ChosenLanguage = '63E62EE8-E073-4C00-8FB1-F1029F8ECED8';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'lv-LV'
WHERE ChosenLanguage = '3953F08A-6CC2-4110-B78E-D1F0D1F63AF5';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'mt-MT'
WHERE ChosenLanguage = '7DC44DBC-5643-4F6B-8DAB-13BE0884BC83';
GO

UPDATE DimCandidate
SET ChosenLanguage = 'sl-SL'
WHERE ChosenLanguage = 'BB1B1CCB-84E2-4E4C-8F14-8B909D566DA4';
GO
