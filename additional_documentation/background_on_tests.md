# Types of questionnaires

## Motivation (Motivational Drive Questionnaire)

### What the test asks

- Hudson's motivation questionnaire helps organizations understand what motivates or demotivates employees or candidates.
- Motivation is essential for performance and engagement, in addition to skill and experience.
- The questionnaire gauges internal and external drives, based on theories such as those of Maslow, Schein, McClelland and Herzberg.
- Results provide insight into developmental priorities and barriers to optimal performance.

### How it is questioned

- Participants are given a series of statements relevant within a professional environment.
- In each case, they must weigh a number of statements that probe both internal and external drivers.

### What's in db

- **ItemId**: The unique ID of the item.
- **Normative Values**: A list of six values, each between 0 and 7, representing the participant's responses to the six statements within that item.

## ARAT (Reasoning Ability)

### General explanation

- **Purpose of reasoning tests**: Provide insight into the cognitive ability and potential of employees or candidates, which correlates with future job performance.
- **Objective measurement**: Reasoning ability is crucial for analyzing and solving problems in the work environment, and must be objectively assessed.
- **Several Tests**:
  - **Abstract Reasoning Ability test**: Measures problem-solving ability in abstract problems; indicator of learning potential.
  - **Numerical Reasoning Ability test**: Measures dealing with numerical information.
  - **Verbal Reasoning Ability test**: Measures dealing with textual information.
  - **Specific Ability Tests**: Focuses on spatial awareness, planning skills, accuracy and technical understanding.
- **Test Format**: All tests consist of problem statements with multiple choice answers.
- **Adapted to job level**: Tests are available at four levels (from worker to senior manager) for optimal experience and relevance.

### How ARAT is questioned

- Participants are presented with problem statements.
- They must indicate the correct answers through a multiple choice format.
- Reasoning tests are tailored to the job level, with variations in complexity and content context.

### What's in db for ARAT

- **TestId**: The ID of the test.
- **ScreenId**: The screen ID.
- **CloneId**: The clone ID.
- **ItemId**: The request ID.
- **Answer**: The answer given by the candidate.
- **CorrectAnswer**: The correct answer.
- **TimeSpent**: The time spent on the question.
- **IsAnswered**: An indicator of whether the question has been answered.
- **IsEmpty**: A readonly property that indicates whether the item is empty (when the ItemId equals 0).

## SJT (Situational Insight - Situational Judgement Test)

### General explanation ARAT

- **Purpose of e-assessments**: Provide an automatic and objective picture of employee or candidate choices in specific situations and whether they match job requirements or organizational values.
- **Simulation of work situations**: E-assessments simulate realistic work situations online, allowing candidates to indicate which responses they find most or least appropriate.
- **Objective evaluation**: The actions chosen are automatically evaluated, allowing an assessment of whether the candidate knows which responses are appropriate for the job.
- **Measurement of competencies and values**: The assessment helps understand the candidate's procedural competencies or values. For example, the competency of “cooperation” assesses whether the candidate chooses actions that promote cooperation.
- **Increase awareness**: The assessments increase employee awareness of the position and help test core organizational values.

### How SJT is questioned

- Participants are confronted with concrete and realistic work situations
- They indicate which responses they find more or less appropriate or which they themselves would prefer.
- The chosen responses are analyzed to determine whether they are in line with the organization's required competencies or values.

### What's in db for SJT

- **SituationId**: 1 (the situation id extracted from the binary data).
- **SequenceIds**: {1, 2, 3} (the sequence IDs, where zeros have been replaced with default values)
- **Answers**: {2, 0, 1} (the answers extracted from the binary data)
- **Scores**: {0, 0, 0} (the scores extracted from the binary data).
- **TimeSpent**: 0 (the time spent, extracted from the binary data)

## PAQ (personality - Personality Assessment Questionnaire)

### General Explanation

- **Purpose of personality questionnaires:**Provide a detailed and objective overview of the personality traits that determine professional behavior and performance.
- **Influence of personality:** Personality influences cooperation, addressing challenges, pursuing goals, dealing with setbacks, and team leadership.
- **Assessment of personality:**It is difficult to gauge personality during an interview; the Hudson questionnaires are designed to do just that.
- **Scientific Basis**: Based on the Big 5 model; participants indicate their behavioral preferences through relevant statements in professional contexts.

### How it is surveyed

- Participants answer a series of statements that gauge their behavioral preferences in various professional situations.

### What's in db for PAQ

- **CodeLeftStatement**: “EMO_15” (the left statement)
- **CodeRightStatement**: “EMO_25” (the right statement)
- **IsInversed**: True (or False, depending on the value in the bit vector).
- **NormativeValue**: 3 (the normative value derived from the bit vector).
- **Score**: 3 (derived from the normative value and whether the value is inverted)

## FCA (feedback)

### General explanation FCA

- **Purpose of Multi-Source Feedback**: Provides a comprehensive picture of employees' professional functioning from different perspectives, which supports them in their development.
- **insight into self-assessment**: It can help to objectify subjective perceptions by collecting feedback from various individuals in the work environment.
- **Exposure of talents and growth potential**: Multi-Source Feedback can be a starting point or calibration point in employee personal development.
- **Quality Feedback**: Multiple evaluators (managers, colleagues, customers, etc.) provide feedback via a qualitative questionnaire based on Hudson's 5+1 competency model.
- **Structure and communication**: A structured approach and transparent communication are crucial to participant engagement and quality feedback.

### How it is surveyed for FCA

- Participants receive a qualitative questionnaire aligned with Hudson's 5+1 competency model.
- Feedback is collected from more than two people, including managers, colleagues and customers.

### What's in db for FCA

- **ItemId**: 15 (the ID of the item).
- **NormativeValues**: [2, 3, 4, 5, 1] (the normative values).
- **IpsativeValues**: [1, 2, 3, 4, 5] (the ipsative values).

## BA51 (behavior)

### General explanation for BAQ

- **Purpose of Simulation Exercises**: Predict the expected behavior of candidates in professional situations so that employees with potential can be identified.
- **behavior and Performance**: Human behavior is often based on habits and patterns. It is important to understand the behaviors that can be expected of employees.
- **Predicting Behavior**: Measuring behavior is challenging; simulation exercises place candidates in relevant, job-related situations to gain immediate insight into their reactions.
- **Realistic practice simulations**: Exercises are contextualized and reference recognizable professional settings, with attention to diversity to avoid stereotyping.
- **Various forms of simulations**: Includes analysis and presentation exercises, role plays, group exercises, mailbox exercises, case studies and speed role plays.
- **Adaptation to job level**: The complexity and content of the simulations are tailored to the job level (from laborer to senior manager).

### How it is questioned BAQ

- **Placement in relevant situations**: Candidates are placed in realistic work scenarios that are objective and job-related.
- **Diversity in content**: Different genders, ages, cultures, nationalities and personalities are considered to avoid stereotyping.
- **behavioral component**: The exercises are designed to minimize prior knowledge of candidates.

### What's in db for BAQ

- **ItemId**: 15 (the ID of the item).
- **NormativeValues**: [2, 3, 4, 5, 1] (the normative values).
- **IpsativeValues**: [1, 2, 3, 4, 5] (the ipsative values).