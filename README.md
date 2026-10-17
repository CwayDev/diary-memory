# diary-memory

A compact persistent memory skill for AI agents across long-running project sessions, following the open [Agent Skills Specification](https://agentskills.io/specification).

Inspired by the OptMem hierarchical folding concept, `diary-memory` saves one-line notes to an append-only diary file. Recent notes are preserved in full, while older notes are hierarchically folded in pairs into concise summaries (blocks of size 2, 4, 8, 16, and so forth, aligned to their size). This guarantees that memory context remains bounded ($O(\log N)$) regardless of how many sessions or notes a project spans.

---

## Folder Structure

```text
diary-memory/
├── SKILL.md                 # Agent skill instructions and workflow definition
├── LICENSE                  # MIT License (2026 Muhammad Alamin Muazu)
├── README.md                # Skill overview, installation, and usage guide
├── scripts/
│   └── memory.py            # Python 3 standard library CLI tool
└── references/
    └── how-it-works.md      # Mathematical folding details and file specifications
```

---

## Installation

You can install `diary-memory` as either a project-specific skill or a global machine-wide skill.

### 1. Antigravity (AGY)
- **Project-level (recommended)**:
  Copy the `diary-memory` folder into your project's `.agents/skills/` directory:
  ```bash
  mkdir -p .agents/skills
  cp -r diary-memory .agents/skills/
  ```
- **Global (all projects on this machine)**:
  Copy into the Antigravity configuration directory:
  - Windows: `%USERPROFILE%\.gemini\config\skills\diary-memory`
  - macOS / Linux: `~/.gemini/config/skills/diary-memory`

### 2. Claude Code and Other Spec-Compliant Agents
- **Project-level**:
  Copy into `.claude/skills/diary-memory`
- **Global**:
  Copy into `~/.claude/skills/diary-memory`

---

## CLI Commands (`scripts/memory.py`)

The helper script requires **Python 3 with standard library only** (no external pip dependencies) and works seamlessly on Windows CMD/PowerShell, macOS, and Linux:

```bash
# Save a one-line note (max 300 characters, secrets rejected)
python scripts/memory.py note "Selected PostgreSQL for user authentication"

# Wake up: display recent 8 notes in full and folded summaries for older notes
python scripts/memory.py wake

# Search all raw notes with case-insensitive regex (max 20 results)
python scripts/memory.py recall "auth"

# Inspect raw notes in index range [LO, HI)
python scripts/memory.py zoom 0 4

# Check which block needs a summary
python scripts/memory.py nap

# Save a synthesized summary for an aligned power-of-two block (max 240 characters)
python scripts/memory.py nap 0 2 "Chose PostgreSQL for auth and configured connection pool"
```

### Environment Variables
- `DIARY_DIR`: Custom directory path for diary files (default: `.diary`).
- `DIARY_KEEP`: Number of recent notes to keep unsummarized (default: `8`).

---

## Validation

To validate that this skill adheres to the Agent Skills specification:

1. Install the reference validator:
   ```bash
   pip install skills-ref
   ```
2. Run validation against the skill folder:
   ```bash
   agentskills validate .
   ```

Expected output:
```text
Valid skill: diary-memory
```

---

## License

MIT License (c) 2026 Muhammad Alamin Muazu. See [LICENSE](LICENSE) for details.
