---
name: revision-checklist
description: Generates structured weekly revision checklists and spaced repetition study schedules with active recall quizzes for university students. Use when a student says help me revise, quiz me, or plan my revision. Use when learners need help balancing study hours across exam subjects, prioritizing difficult topics, and staying accountable. Do not use for completing graded homework, writing submitted essays, solving exam questions directly, or bypassing academic integrity standards.
license: MIT
---

# Weekly Revision Checklist

Helps students build structured weekly revision plans, calculate balanced study hours based on topic difficulty, and prepare active recall self-quizzes.

For cognitive revision principles and spaced repetition details, see [study-methodology.md](references/study-methodology.md).
Study session allocation tool is located at [plan_schedule.py](scripts/plan_schedule.py).

## When to Use

Activate this skill when:
- A student requests a study schedule (e.g. "help me revise for my finals", "plan my revision for this week").
- A student asks for diagnostic self-testing (e.g. "quiz me on organic chemistry", "test my understanding").
- A student feels overwhelmed by multiple subjects and needs a clear study breakdown.

## What to Gather First

Before creating the checklist, ask the student for four key inputs:
1. **Subjects / Topics**: List of specific modules or exam topics to cover.
2. **Confidence Level**: Rating from 1 (lowest confidence/hardest) to 5 (comfortable) for each topic.
3. **Weekly Hours**: Total realistic study hours available this week.
4. **Deadlines**: Any upcoming exam or test dates within the next 2-3 weeks.

## Step-by-Step Process

### 1. Calculate Time Budget
Run the scheduling helper script to calculate balanced study hours:
```bash
python scripts/plan_schedule.py --hours <TOTAL_HOURS> --topics "<TOPIC_1>:<CONFIDENCE>[:<DAYS>],<TOPIC_2>:<CONFIDENCE>[:<DAYS>]"
```
- Topics with lower confidence (1-2) automatically receive higher weekly hour allocations.
- Topics with exams within 7 days receive urgency warnings.

### 2. Generate Active Recall Prompts
For each topic, formulate 3 to 5 conceptual self-testing prompts:
- Focus on mechanisms, contrasts, and problem-solving principles rather than trivial trivia.
- Frame prompts as open-ended questions (e.g. "Explain why X happens when Y changes").

### 3. Build the Weekly Revision Checklist
Construct a Markdown schedule organized by day (Monday to Sunday) containing:
- Specific focus topics for each day.
- Designated study duration (e.g. 2 x 45-min Pomodoro sessions).
- 2-3 active recall questions to answer closed-book.
- Spaced repetition check-in dates (Day 1, 3, 7 review intervals).

### 4. Interactive Self-Quizzing
When the user asks to be quizzed:
- Pose one question at a time.
- Wait for the student's attempt before evaluating.
- Provide encouraging feedback and highlight missed nuances without giving away direct exam solutions.

## Output Format

Present the plan in this structured format:

### Weekly Study Allocation
| Subject / Topic | Confidence (1-5) | Allocated Hours | Sessions | Urgency |
| :--- | :--- | :--- | :--- | :--- |
| Topic A | 2 | 4.5h | 3 sessions | Medium |
| Topic B | 4 | 2.0h | 1 session | Normal |

### Daily Action Checklist
- [ ] **Monday (2.0h - Topic A)**: Review core mechanisms; complete 3 practice problems.
  - *Active Recall Prompt*: Explain the rate-limiting step without opening slides.
- [ ] **Tuesday (1.5h - Topic B)**: Summary cheat-sheet synthesis; flashcard review round 1.
- [ ] **Wednesday (2.0h - Topic A Spaced Review)**: Closed-book diagnostic quiz.

## Strict Rules and Prohibitions

- **NO Graded Homework**: Never complete graded assignments, lab reports, or take-home tests.
- **NO Direct Answers During Quizzes**: Never reveal the answers before the student attempts the question.
- **NO Unrealistic Schedules**: Do not allocate more than 6-8 focused study hours per day.
- **NO Passive Tasks**: Avoid vague tasks like "read chapter 4". Frame every task as active (e.g. "summarize chapter 4 key formulas from memory").
