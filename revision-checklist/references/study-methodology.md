# Revision Methodology and Study Science

Effective revision relies on evidence-based cognitive psychology principles rather than passive re-reading or highlighted notes.

---

## 1. Confidence-Weighted Time Allocation

When preparing for exams across multiple subjects, students often spend disproportionate time on topics they already understand. The `plan_schedule.py` script applies an inverse-weighting formula:

$$\text{Weight}(T) = 6 - \text{Confidence}(T)$$

Where $\text{Confidence} \in \{1, 2, 3, 4, 5\}$:
- Confidence 1 (High difficulty / low mastery) receives weight 5.
- Confidence 5 (Mastered / high comfort) receives weight 1.

The weekly hour allocation for topic $i$ is:
$$\text{Hours}_i = \frac{\text{Weight}_i}{\sum_j \text{Weight}_j} \times \text{Total Hours}$$

Urgency boosts are applied if an exam occurs within 3 to 7 days.

---

## 2. Active Recall over Passive Review

Passive review (reading lecture slides, highlighting notes) gives a false illusion of competence. Active recall forces the brain to retrieve information from memory:

- **Feynman Technique**: Explain a complex concept in plain words without jargon as if teaching a beginner.
- **Closed-Book Brain Dumps**: Spend 10 minutes writing everything remembered about a concept before opening notes.
- **Diagnostic Self-Quizzing**: Transform syllabus learning objectives into open-ended questions.

---

## 3. Spaced Repetition Intervals

To counter the Ebbinghaus forgetting curve, schedule reviews at increasing intervals:

| Review Round | Timing | Primary Activity |
| :--- | :--- | :--- |
| **Initial Study** | Day 0 | Understand core concepts, create 5-10 flashcards or recall prompts |
| **First Review** | Day 1 (+24 hours) | Rapid recall quiz; review missed questions |
| **Second Review** | Day 3 | Application problem or practice question |
| **Third Review** | Day 7 | Timed past paper question or concept synthesis |
| **Consolidation** | Day 14 | Rapid summary review and self-test |

---

## 4. Academic Integrity Guardrails

This skill functions as a study coach and revision architect, **not** an academic evasion tool:
- Never generate answers to graded homework, ongoing assessments, or take-home quizzes.
- Offer diagnostic hints and concept explanations rather than completed solutions.
