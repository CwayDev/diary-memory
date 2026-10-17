# How diary-memory Works

`diary-memory` provides persistent, compact memory across AI agent sessions. It is inspired by the OptMem hierarchical folding concept, ensuring that context stays small regardless of how long a project runs.

---

## 1. File Formats and Storage

By default, all diary files are stored in the `.diary/` directory at the project root (or at the path specified by the `DIARY_DIR` environment variable).

### `LOG.txt`
- **Purpose**: Append-only log of raw notes.
- **Format**: Tab-separated values (`\t`), one line per note:
  ```text
  <id>\t<date>\t<text>\n
  ```
- **Fields**:
  - `id`: Zero-based integer index (`0`, `1`, `2`, ...).
  - `date`: Date when the note was recorded (`YYYY-MM-DD`).
  - `text`: One-line note text (maximum 300 characters, whitespace normalized, no newlines or tabs).
- **Invariants**: Notes are strictly append-only. Past notes are never deleted or rewritten.

### `SUMMARIES.txt`
- **Purpose**: Cache of hierarchical folded summaries.
- **Format**: Tab-separated values (`\t`), one line per summary block:
  ```text
  <lo>\t<hi>\t<text>\n
  ```
- **Fields**:
  - `lo`: Inclusive start note ID of the block.
  - `hi`: Exclusive end note ID of the block.
  - `text`: One-line summary (maximum 240 characters).
- **Semantics**: Newest line wins. If multiple lines exist for the same `[lo, hi)` block, the latest entry takes precedence.

---

## 2. Power-of-Two Hierarchical Folding

To prevent memory from growing unboundedly, notes outside the recent window are folded hierarchically into power-of-two aligned blocks:

- **Block Size**: Must be a power of two ($2, 4, 8, 16, 32, \dots$).
- **Alignment**: For a block of size $S$, the starting index `lo` must satisfy:
  $$\text{lo} \pmod S = 0 \quad \text{and} \quad \text{hi} = \text{lo} + S$$
  Examples of valid blocks:
  - Size 2: `[0, 2)`, `[2, 4)`, `[4, 6)`, `[6, 8)`
  - Size 4: `[0, 4)`, `[4, 8)`, `[8, 12)`
  - Size 8: `[0, 8)`, `[8, 16)`
- **Bottom-Up Composition**:
  - A block of size 2 folds two raw notes.
  - A block of size $S$ ($S \ge 4$) merges its two summarized halves: `[lo, lo + S/2)` and `[lo + S/2, hi)`. A larger block is only eligible for summarization after both child halves already have summaries.

### The Recent Window (`DIARY_KEEP`)
- The newest $K$ notes (default: 8, configured via `DIARY_KEEP`) remain unsummarized in their raw form.
- The cutoff boundary is $W = \max(0, N - K)$, where $N$ is total notes.
- Only notes before index $W$ (i.e. `hi <= W`) are eligible for summarization.
- As new notes are added, older notes shift outside the recent window and trigger folding prompts.

### Complexity & Size Guarantee
For $N$ total notes and keep window $K$:
- Recent notes: at most $K$ lines.
- Summarized history: at most $O(\log_2 N)$ lines.
- Even after 1,000 notes, `wake` outputs fewer than 20 lines.

---

## 3. Settings and Configuration

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DIARY_DIR` | `.diary` | Path to directory where `LOG.txt` and `SUMMARIES.txt` live. |
| `DIARY_KEEP` | `8` | Number of most recent notes to show in full without folding. |

### Privacy and Version Control
- **Shared Team Diary**: Commit `.diary/` to Git so all team members and agents share memory.
- **Private Local Diary**: Add `.diary/` to `.gitignore` to keep memories private on your local machine.

---

## 4. Security Guardrails

The memory tool enforces strict secret filtering:
- Automatically rejects passwords, tokens, API keys (OpenAI, Anthropic, Google, AWS, GitHub, Slack), and private keys.
- Limits notes to 300 characters and summaries to 240 characters to discourage pasting conversational transcripts or large code snippets.
