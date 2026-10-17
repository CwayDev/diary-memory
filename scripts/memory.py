#!/usr/bin/env python3
"""
diary-memory: persistent hierarchical memory across AI agent sessions.
Standard library only. Compatible with Windows CMD/PowerShell, macOS, and Linux.
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Character limits
MAX_NOTE_LEN = 300
MAX_SUMMARY_LEN = 240
MAX_RECALL_RESULTS = 20

# Secret detection regexes
SECRET_PATTERNS = [
    (r"(?i)\b(sk-[a-zA-Z0-9]{20,})\b", "OpenAI/Stripe API key"),
    (r"\bAIza[0-9A-Za-z-_]{35}\b", "Google API key"),
    (r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b", "GitHub personal access token"),
    (r"\bgithub_pat_[A-Za-z0-9_]{22,}\b", "GitHub fine-grained token"),
    (r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b", "Slack token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key ID"),
    (r"(?i)\bbearer\s+[a-zA-Z0-9_\-\.]{20,}\b", "Bearer authentication token"),
    (r"-----BEGIN[ A-Z0-9_-]*PRIVATE KEY-----", "Private cryptographic key"),
    (
        r"(?i)\b(password|passwd|api[_-]?key|access[_-]?token|auth[_-]?token|secret)\s*[:=]\s*['\"]?[^\s'\"]{8,}",
        "Credential or token assignment",
    ),
    (
        r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+\b",
        "JSON Web Token (JWT)",
    ),
]


def detect_secret(text: str) -> str | None:
    """Return description of detected secret pattern, or None if safe."""
    for pattern, desc in SECRET_PATTERNS:
        if re.search(pattern, text):
            return desc
    return None


def get_diary_dir() -> Path:
    """Return the diary directory path, defaulting to .diary in current working directory."""
    raw = os.environ.get("DIARY_DIR", ".diary")
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_diary_keep() -> int:
    """Return DIARY_KEEP setting (default 8)."""
    val = os.environ.get("DIARY_KEEP", "8")
    try:
        keep = int(val)
        return max(1, keep)
    except ValueError:
        return 8


def get_log_path() -> Path:
    return get_diary_dir() / "LOG.txt"


def get_summaries_path() -> Path:
    return get_diary_dir() / "SUMMARIES.txt"


def load_notes() -> list[dict]:
    """Load raw notes from LOG.txt. Each item: {'id': int, 'date': str, 'text': str}."""
    log_file = get_log_path()
    if not log_file.exists():
        return []
    notes = []
    with log_file.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split("\t", 2)
            if len(parts) == 3:
                try:
                    nid = int(parts[0])
                    notes.append({"id": nid, "date": parts[1], "text": parts[2]})
                except ValueError:
                    continue
            elif len(parts) == 2:
                # Fallback if id is omitted
                notes.append({"id": line_num, "date": parts[0], "text": parts[1]})
    return notes


def load_summaries() -> dict[tuple[int, int], str]:
    """Load summaries from SUMMARIES.txt. Newest line wins for identical (lo, hi)."""
    sum_file = get_summaries_path()
    if not sum_file.exists():
        return {}
    summaries = {}
    with sum_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split("\t", 2)
            if len(parts) == 3:
                try:
                    lo = int(parts[0])
                    hi = int(parts[1])
                    text = parts[2]
                    summaries[(lo, hi)] = text
                except ValueError:
                    continue
    return summaries


def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def find_needed_summary(
    notes_count: int, summaries: dict[tuple[int, int], str], keep: int
) -> tuple[int, int, int] | None:
    """
    Find the smallest aligned power-of-two block outside the recent window
    that still needs a summary. Returns (lo, hi, size) or None.
    A bigger block only needs a summary after both of its halves have summaries.
    """
    cutoff = notes_count - keep
    if cutoff < 2:
        return None

    # Check sizes 2, 4, 8, 16, 32, ...
    size = 2
    while size <= cutoff:
        # Check all aligned blocks of this size within [0, cutoff]
        lo = 0
        while lo + size <= cutoff:
            hi = lo + size
            if (lo, hi) not in summaries:
                # If size == 2, it needs a summary if raw notes exist
                if size == 2:
                    return (lo, hi, size)
                # If size > 2, both halves must already have summaries
                mid = lo + size // 2
                if (lo, mid) in summaries and (mid, hi) in summaries:
                    return (lo, hi, size)
            lo += size
        size *= 2

    return None


def sanitize_text(text: str) -> str:
    """Normalize whitespace and strip tab / newline characters."""
    return " ".join(text.strip().split())


def cmd_note(args: list[str]) -> None:
    if not args:
        print(
            "Error: Note text is missing.\n"
            "What to do next: Provide your note as an argument, for example:\n"
            '  python scripts/memory.py note "Decided to use PostgreSQL for user auth"'
        )
        sys.exit(1)

    raw_text = " ".join(args)
    clean_text = sanitize_text(raw_text)

    if not clean_text:
        print(
            "Error: Note text cannot be empty or whitespace only.\n"
            "What to do next: Provide a meaningful one-line note (max 300 characters)."
        )
        sys.exit(1)

    if len(clean_text) > MAX_NOTE_LEN:
        print(
            f"Error: Note exceeds maximum length of {MAX_NOTE_LEN} characters (got {len(clean_text)}).\n"
            f"What to do next: Shorten the note to under {MAX_NOTE_LEN} characters and run the command again."
        )
        sys.exit(1)

    secret_type = detect_secret(clean_text)
    if secret_type:
        print(
            f"Error: Note appears to contain sensitive information ({secret_type}).\n"
            "What to do next: Remove secrets, tokens, or passwords from the note. "
            "diary-memory strictly forbids storing credentials."
        )
        sys.exit(1)

    log_file = get_log_path()
    notes = load_notes()
    next_id = len(notes)
    today = datetime.now().strftime("%Y-%m-%d")

    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"{next_id}\t{today}\t{clean_text}\n")

    print(f"Saved note #{next_id}: {clean_text}")

    # Check if a summary is needed
    keep = get_diary_keep()
    summaries = load_summaries()
    needed = find_needed_summary(len(notes) + 1, summaries, keep)
    if needed:
        n_lo, n_hi, _ = needed
        print(
            f"SUMMARY NEEDED for block [{n_lo}-{n_hi})\n"
            "What to do next: Run 'python scripts/memory.py nap' to view items and create this summary."
        )


def decompose_range_to_blocks(lo: int, hi: int) -> list[tuple[int, int]]:
    """
    Decompose [lo, hi) into the biggest aligned power-of-two blocks.
    """
    blocks = []
    pos = lo
    while pos < hi:
        # Find maximum power-of-two size S such that pos % S == 0 and pos + S <= hi
        rem = hi - pos
        s = 1
        while (pos % (s * 2) == 0) and (pos + s * 2 <= hi):
            s *= 2
        blocks.append((pos, pos + s))
        pos += s
    return blocks


def render_block(
    lo: int,
    hi: int,
    summaries: dict[tuple[int, int], str],
    notes_by_id: dict[int, dict],
) -> list[str]:
    """
    Render block [lo, hi). If summary exists, return it.
    Otherwise fall back recursively to smaller blocks down to raw notes.
    """
    size = hi - lo
    if (lo, hi) in summaries:
        return [f"[Block {lo}-{hi}]: {summaries[(lo, hi)]}"]

    if size == 1:
        note = notes_by_id.get(lo)
        if note:
            return [f"#{note['id']} [{note['date']}]: {note['text']}"]
        return [f"#{lo} [unknown]: <missing note>"]

    # Fall back to two halves
    mid = lo + size // 2
    left = render_block(lo, mid, summaries, notes_by_id)
    right = render_block(mid, hi, summaries, notes_by_id)
    return left + right


def cmd_wake(_args: list[str]) -> None:
    notes = load_notes()
    if not notes:
        print(
            "Diary is empty.\n"
            "What to do next: Use 'python scripts/memory.py note \"<text>\"' to record your first note."
        )
        return

    keep = get_diary_keep()
    summaries = load_summaries()
    total = len(notes)
    notes_by_id = {n["id"]: n for n in notes}

    cutoff = max(0, total - keep)

    output_lines = []

    # 1. Older notes outside recent window
    if cutoff > 0:
        blocks = decompose_range_to_blocks(0, cutoff)
        for b_lo, b_hi in blocks:
            lines = render_block(b_lo, b_hi, summaries, notes_by_id)
            output_lines.extend(lines)

    # 2. Recent notes in full
    recent_notes = notes[cutoff:]
    for n in recent_notes:
        output_lines.append(f"#{n['id']} [{n['date']}]: {n['text']}")

    for line in output_lines:
        print(line)

    # Check if a summary is needed
    needed = find_needed_summary(total, summaries, keep)
    if needed:
        n_lo, n_hi, _ = needed
        print(
            f"\nSUMMARY NEEDED for block [{n_lo}-{n_hi})\n"
            "What to do next: Run 'python scripts/memory.py nap' to view items and create this summary."
        )


def cmd_recall(args: list[str]) -> None:
    if not args:
        print(
            "Error: Search pattern is missing.\n"
            "What to do next: Provide a regex pattern or keyword, for example:\n"
            "  python scripts/memory.py recall auth"
        )
        sys.exit(1)

    pattern_str = " ".join(args)
    try:
        regex = re.compile(pattern_str, re.IGNORECASE)
    except re.error as e:
        print(
            f"Error: Invalid regular expression pattern '{pattern_str}': {e}.\n"
            "What to do next: Provide a valid regex pattern or simple keyword."
        )
        sys.exit(1)

    notes = load_notes()
    if not notes:
        print(
            "Diary is empty.\n"
            "What to do next: Record notes with 'python scripts/memory.py note \"<text>\"' before searching."
        )
        return

    matches = [n for n in notes if regex.search(n["text"])]
    if not matches:
        print(
            f"No notes matched pattern '{pattern_str}'.\n"
            "What to do next: Try a broader search keyword or run 'python scripts/memory.py wake' to review recent context."
        )
        return

    count = len(matches)
    shown = matches[:MAX_RECALL_RESULTS]
    print(f"Found {count} matching note(s) (showing {len(shown)}):")
    for n in shown:
        print(f"  #{n['id']} [{n['date']}]: {n['text']}")

    if count > MAX_RECALL_RESULTS:
        print(
            f"\nNote: Truncated at {MAX_RECALL_RESULTS} results.\n"
            "What to do next: Refine your regex pattern to narrow down the search results."
        )


def cmd_zoom(args: list[str]) -> None:
    if len(args) != 2:
        print(
            "Error: zoom requires exactly two arguments: LO and HI.\n"
            "What to do next: Provide range boundaries, for example:\n"
            "  python scripts/memory.py zoom 0 4"
        )
        sys.exit(1)

    try:
        lo = int(args[0])
        hi = int(args[1])
    except ValueError:
        print(
            f"Error: LO and HI must be integers, got '{args[0]}' and '{args[1]}'.\n"
            "What to do next: Run with integer indices, e.g. 'python scripts/memory.py zoom 0 4'."
        )
        sys.exit(1)

    if lo < 0 or hi <= lo:
        print(
            f"Error: Invalid range [{lo}, {hi}). LO must be non-negative and less than HI.\n"
            "What to do next: Provide a valid range where LO < HI (e.g. 'zoom 0 4')."
        )
        sys.exit(1)

    notes = load_notes()
    if not notes:
        print(
            "Diary is empty.\n"
            "What to do next: Record notes with 'python scripts/memory.py note \"<text>\"'."
        )
        return

    notes_by_id = {n["id"]: n for n in notes}
    matched = [notes_by_id[i] for i in range(lo, hi) if i in notes_by_id]

    if not matched:
        print(
            f"No notes found in range [{lo}, {hi}). Total available note IDs: 0 to {len(notes) - 1}.\n"
            "What to do next: Check the note indices and select a range within 0 to {len(notes)}."
        )
        return

    print(f"Notes in range [{lo}, {hi}):")
    for n in matched:
        print(f"  #{n['id']} [{n['date']}]: {n['text']}")


def cmd_nap(args: list[str]) -> None:
    notes = load_notes()
    summaries = load_summaries()
    keep = get_diary_keep()
    total = len(notes)
    cutoff = total - keep

    # Mode 1: Check what needs summary
    if len(args) == 0:
        needed = find_needed_summary(total, summaries, keep)
        if not needed:
            print(
                "All eligible older blocks outside the recent window are already summarized.\n"
                "What to do next: Continue working and adding notes; run 'nap' again when prompted."
            )
            return

        lo, hi, size = needed
        print(f"SUMMARY NEEDED for block [{lo}-{hi})")
        if size == 2:
            notes_by_id = {n["id"]: n for n in notes}
            print("Raw notes to merge into a single one-line summary:")
            for nid in (lo, lo + 1):
                n = notes_by_id.get(nid)
                if n:
                    print(f"  #{n['id']} [{n['date']}]: {n['text']}")
                else:
                    print(f"  #{nid}: <missing>")
        else:
            mid = lo + size // 2
            print("Child summaries to merge into a single one-line summary:")
            print(f"  Block [{lo}-{mid}): {summaries.get((lo, mid), '<missing>')}")
            print(f"  Block [{mid}-{hi}): {summaries.get((mid, hi), '<missing>')}")

        print(
            "\nWhat to do next: Write a one-line summary (max 240 chars) and run:\n"
            f'  python scripts/memory.py nap {lo} {hi} "<summary text>"'
        )
        return

    # Mode 2: Save summary: nap LO HI "TEXT"
    if len(args) < 3:
        print(
            "Error: Invalid nap arguments.\n"
            "What to do next:\n"
            "  - Run 'python scripts/memory.py nap' without arguments to see which block needs summarizing.\n"
            '  - Or run \'python scripts/memory.py nap LO HI "TEXT"\' to save a summary.'
        )
        sys.exit(1)

    try:
        lo = int(args[0])
        hi = int(args[1])
    except ValueError:
        print(
            f"Error: Block boundaries LO and HI must be integers, got '{args[0]}' and '{args[1]}'.\n"
            "What to do next: Provide integer block indices, e.g. 'nap 0 2 \"text\"'."
        )
        sys.exit(1)

    raw_text = " ".join(args[2:])
    clean_text = sanitize_text(raw_text)

    if not clean_text:
        print(
            "Error: Summary text cannot be empty.\n"
            "What to do next: Provide a meaningful summary (max 240 characters)."
        )
        sys.exit(1)

    if len(clean_text) > MAX_SUMMARY_LEN:
        print(
            f"Error: Summary exceeds maximum length of {MAX_SUMMARY_LEN} characters (got {len(clean_text)}).\n"
            f"What to do next: Shorten the summary to under {MAX_SUMMARY_LEN} characters and run again."
        )
        sys.exit(1)

    secret_type = detect_secret(clean_text)
    if secret_type:
        print(
            f"Error: Summary appears to contain sensitive information ({secret_type}).\n"
            "What to do next: Remove secrets, tokens, or passwords from the summary."
        )
        sys.exit(1)

    size = hi - lo
    if lo < 0 or hi <= lo or not is_power_of_two(size):
        print(
            f"Error: Block [{lo}, {hi}) size ({size}) is not a power of two (2, 4, 8, 16, ...).\n"
            "What to do next: Use aligned power-of-two boundaries. Run 'nap' without arguments to inspect."
        )
        sys.exit(1)

    if lo % size != 0:
        aligned_lo = lo - (lo % size)
        print(
            f"Error: Block [{lo}, {hi}) is not aligned to its size {size} (LO % size != 0).\n"
            f"What to do next: Align LO to a multiple of {size} (e.g. [{aligned_lo}, {aligned_lo + size}])."
        )
        sys.exit(1)

    if hi > cutoff:
        if cutoff == 0:
            print(
                f"Error: Block [{lo}, {hi}) cannot be summarized because there are only {total} note(s) in total, "
                f"all of which fall inside the recent window (newest {keep} notes).\n"
                f"What to do next: Add at least {keep + size - total} more note(s) before summarizing this block."
            )
        else:
            print(
                f"Error: Block [{lo}, {hi}) overlaps the recent window (notes {cutoff} to {total - 1}).\n"
                f"What to do next: Only older notes outside the newest {keep} notes can be summarized. "
                "Add more notes before attempting to summarize this block."
            )
        sys.exit(1)

    if size > 2:
        mid = lo + size // 2
        if (lo, mid) not in summaries or (mid, hi) not in summaries:
            print(
                f"Error: Cannot summarize [{lo}, {hi}) because its child halves [{lo}, {mid}) and [{mid}, {hi}) are not both summarized.\n"
                "What to do next: Run 'python scripts/memory.py nap' to summarize child blocks first."
            )
            sys.exit(1)

    sum_file = get_summaries_path()
    with sum_file.open("a", encoding="utf-8") as f:
        f.write(f"{lo}\t{hi}\t{clean_text}\n")

    print(f"Saved summary for block [{lo}, {hi}): {clean_text}")

    # Reload summaries and check if next block needs summary
    summaries[(lo, hi)] = clean_text
    next_needed = find_needed_summary(total, summaries, keep)
    if next_needed:
        n_lo, n_hi, _ = next_needed
        print(
            f"SUMMARY NEEDED for block [{n_lo}-{n_hi})\n"
            "What to do next: Run 'python scripts/memory.py nap' to view items and create this summary."
        )


def print_help() -> None:
    print(
        "diary-memory: persistent memory across agent sessions\n\n"
        "Usage:\n"
        "  python scripts/memory.py note TEXT      Append one line note (max 300 chars, no secrets)\n"
        "  python scripts/memory.py wake           Show recent notes and folded older summaries\n"
        "  python scripts/memory.py recall PAT     Regex search across all raw notes (max 20)\n"
        "  python scripts/memory.py zoom LO HI     Show raw notes in index range [LO, HI)\n"
        "  python scripts/memory.py nap            Print smallest block needing a summary\n"
        '  python scripts/memory.py nap LO HI "T"  Save one-line summary (max 240 chars) for block [LO, HI)\n\n'
        "Environment variables:\n"
        "  DIARY_DIR   Path to diary storage folder (default: .diary)\n"
        "  DIARY_KEEP  Number of newest notes to keep unsummarized (default: 8)"
    )


def main() -> None:
    # Ensure stdout handles UTF-8 on Windows
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "note":
        cmd_note(args)
    elif cmd == "wake":
        cmd_wake(args)
    elif cmd == "recall":
        cmd_recall(args)
    elif cmd == "zoom":
        cmd_zoom(args)
    elif cmd == "nap":
        cmd_nap(args)
    else:
        print(
            f"Error: Unknown command '{cmd}'.\n"
            "What to do next: Use one of: note, wake, recall, zoom, nap. "
            "Run 'python scripts/memory.py --help' for usage details."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
