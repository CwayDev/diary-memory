# revision-checklist

An AI agent skill following the open [Agent Skills Specification](https://agentskills.io/specification) to help university students build structured weekly revision checklists, balance study hours, and conduct active recall self-quizzing.

---

## Folder Structure

```text
revision-checklist/
├── SKILL.md                 # Agent skill instructions and study workflow definition
├── LICENSE                  # MIT License (2026 Muhammad Alamin Muazu)
├── README.md                # Installation and usage instructions
├── scripts/
│   └── plan_schedule.py     # Python 3 CLI tool for time allocation & spaced review
└── references/
    └── study-methodology.md # Scientific revision principles and active recall guides
```

---

## Installation

### 1. Antigravity (AGY)
- **Project-level**:
  Copy the folder into `.agents/skills/`:
  ```bash
  mkdir -p .agents/skills
  cp -r revision-checklist .agents/skills/
  ```
- **Global**:
  Copy to `%USERPROFILE%\.gemini\config\skills\revision-checklist` (Windows) or `~/.gemini/config/skills/revision-checklist` (macOS/Linux).

### 2. Claude Code & Open Spec Agents
- **Project-level**: `.claude/skills/revision-checklist`
- **Global**: `~/.claude/skills/revision-checklist`

---

## CLI Usage (`scripts/plan_schedule.py`)

Standard library Python 3 only (no third-party dependencies required):

```bash
# Calculate weekly study hour breakdown based on topic confidence and exam dates
python scripts/plan_schedule.py --hours 15 --topics "Calculus:2:10,Organic Chemistry:1:5,History:4:20"
```

### Parameters
- `--hours`: Total available study hours for the upcoming week.
- `--topics`: Comma-separated list of topics in format `Topic:Confidence[:DaysUntilExam]` (confidence is 1 to 5).
- `--start-date`: Optional start date in `YYYY-MM-DD` format (defaults to today).

---

## Validation

Validate this skill with the reference validator:

```bash
pip install skills-ref
agentskills validate ./revision-checklist
```

Expected output:
```text
Valid skill: revision-checklist
```

---

## License

MIT License (c) 2026 Muhammad Alamin Muazu. See [LICENSE](LICENSE) for details.
