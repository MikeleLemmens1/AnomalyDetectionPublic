# Data exploration

I start with importing the backup file provided by the customer. I notice there is a central entity (Candidate), and a seperate table for each test. It seems that there are 6 tests:

- ARAT
- BA51
- FCA
- Motivation
- PAQ
- SJT

Each test has some metadata stored in the DB (creation date,...) and one column contains all the data in binary form. This binary form needs to be extracted, transformed and stored to be used later on. Every test has a CandidateID that acts like a foreign key, but they are not actually used like this in the database. I assume a candidate will have at least one test. Here are all colums per table:

| Candidate         | ARAT             | BA51          | FCA                      | Motivation               | PAQ           | SJT           |
| :---------------- | :--------------- | :------------ | :----------------------- | :----------------------- | :------------ | :------------ |
| ID                | ID               | ID            | ID                       | ID                       | ID            | ID            |
| InstanceID        | CandidateID      | CandidateID   | CandidateID              | CandidateID              | CandidateID   | CandidateID   |
| AssessmentGUID    | InstanceID       | InstanceID    | InstanceID               | InstanceID               | InstanceID    | InstanceID    |
| OrganizationGUID  | Data             | Data          | Data                     | Data                     | Data          | Data          |
| Gender            | CreatedDate      | CreatedDate   | CreatedDate              | CreatedDate              | CreatedDate   | CreatedDate   |
| GenderChoice      | ModifiedDate     | ModifiedDate  | ModifiedDate             | ModifiedDate             | ModifiedDate  | ModifiedDate  |
| Qualification     | VersionNumber    | VersionNumber | VersionNumber            | VersionNumber            | VersionNumber | VersionNumber |
| InstrumentClassID | TestStartTime    | IsExported    | TestStartTime            | TestStartTime            | DataReg       | IsExported    |
| LanguageGUID      | TestFinishTime   |               | TestFinishTime           | TestFinishTime           | IsExported    |               |
|                   | IsExported       |               | DataPlanning             | DataPlanning             |               |               |
|                   | IntermediateData |               | IntermediateData         | IntermediateData         |               |               |
|                   | PostedDate       |               | IntermediateDataPlanning | IntermediateDataPlanning |               |               |
|                   |                  | PostedDate    | PostedDate               |                          |               |               |

TODO:

- [ ] Check for the earliest date and create a DimDate table
- [ ] Implement a way of transforming the given data to load in our DWH
- [ ] Can we label the results in any way? Good or bad candidate? I assume most of these tests don't have a certain summarizing score
- [ ] Learn about the nature of the tests (!)

Questions about the data

- What do the following attributes mean?
  - DataPlanning
  - IntermediateData
  - IntermediateDataPlanning
