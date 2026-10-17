#!/usr/bin/env python3
"""
plan_schedule.py: Study session and spaced repetition scheduler for university students.
Standard library only. Compatible with Windows, macOS, and Linux.
"""

import argparse
import sys
from datetime import datetime, timedelta


def parse_topic_entry(entry: str) -> dict:
    """
    Parse a topic entry in format 'Name:Confidence' or 'Name:Confidence:DaysUntilExam'.
    Confidence is 1 (lowest confidence/hardest) to 5 (highest confidence/mastered).
    """
    parts = entry.split(":")
    name = parts[0].strip()
    if not name:
        raise ValueError("Topic name cannot be empty.")

    confidence = 3
    if len(parts) >= 2:
        try:
            confidence = int(parts[1])
            if confidence < 1 or confidence > 5:
                raise ValueError
        except ValueError:
            raise ValueError(f"Confidence for '{name}' must be an integer between 1 and 5 (got '{parts[1]}').")

    days_until_exam = None
    if len(parts) >= 3:
        try:
            days_until_exam = int(parts[2])
            if days_until_exam < 1:
                raise ValueError
        except ValueError:
            raise ValueError(f"Days until exam for '{name}' must be a positive integer (got '{parts[2]}').")

    return {
        "name": name,
        "confidence": confidence,
        "days": days_until_exam,
    }


def compute_spaced_repetition(days_ahead: int = 14) -> list[int]:
    """Return standard spaced repetition review days up to days_ahead."""
    intervals = [1, 3, 7, 14, 21, 30]
    return [i for i in intervals if i <= days_ahead]


def allocate_hours(topics: list[dict], total_hours: float) -> list[dict]:
    """
    Allocate weekly study hours inversely proportional to confidence score.
    A lower confidence (e.g. 1) receives higher weight than high confidence (e.g. 5).
    """
    # Inverse weights: 1 -> 5, 2 -> 4, 3 -> 3, 4 -> 2, 5 -> 1
    weights = [6 - t["confidence"] for t in topics]
    total_weight = sum(weights)

    results = []
    for t, w in zip(topics, weights):
        hours = round((w / total_weight) * total_hours, 1)
        # Urgency multiplier if exam is within 7 days
        urgency = "Normal"
        if t["days"] is not None:
            if t["days"] <= 3:
                urgency = "High (Exam in <= 3 days)"
            elif t["days"] <= 7:
                urgency = "Medium (Exam this week)"

        results.append({
            "name": t["name"],
            "confidence": t["confidence"],
            "days_until_exam": t["days"],
            "urgency": urgency,
            "allocated_hours": hours,
            "sessions_per_week": max(1, round(hours / 1.5)),  # approx 1.5h per session
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate study time allocation and spaced repetition schedule for weekly revision.",
        epilog="Example: python scripts/plan_schedule.py --hours 12 --topics \"Calculus:2:10,Organic Chemistry:1:5,History:4:20\"",
    )
    parser.add_argument(
        "--hours",
        type=float,
        required=True,
        help="Total available study hours for the upcoming week (e.g. 10, 15.5).",
    )
    parser.add_argument(
        "--topics",
        type=str,
        required=True,
        help="Comma-separated topics in 'Name:Confidence[:DaysUntilExam]' format. Confidence is 1 to 5.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date for revision week in YYYY-MM-DD format (default: today).",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        print("\nWhat to do next: Provide --hours and --topics to generate a revision plan.")
        sys.exit(0)

    try:
        args = parser.parse_args()
    except SystemExit:
        print("\nWhat to do next: Check the argument format above and run the command again.")
        sys.exit(1)

    if args.hours <= 0:
        print(
            "Error: Study hours must be greater than zero.\n"
            "What to do next: Provide a realistic weekly study budget, e.g. '--hours 10'."
        )
        sys.exit(1)

    raw_topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    if not raw_topics:
        print(
            "Error: No topics provided.\n"
            "What to do next: Provide at least one topic, e.g. '--topics \"Data Structures:2\"'."
        )
        sys.exit(1)

    parsed_topics = []
    for item in raw_topics:
        try:
            parsed_topics.append(parse_topic_entry(item))
        except ValueError as e:
            print(f"Error: {e}\nWhat to do next: Use format 'TopicName:Confidence(1-5)[:DaysUntilExam]'.")
            sys.exit(1)

    start_dt = datetime.now()
    if args.start_date:
        try:
            start_dt = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print(
                f"Error: Invalid start date format '{args.start_date}'.\n"
                "What to do next: Use YYYY-MM-DD format, e.g. '--start-date 2026-10-20'."
            )
            sys.exit(1)

    allocations = allocate_hours(parsed_topics, args.hours)

    print("=== WEEKLY REVISION TIME ALLOCATION ===")
    print(f"Total Budget: {args.hours:.1f} hours | Start Date: {start_dt.strftime('%Y-%m-%d')}\n")
    print(f"{'Topic':<25} {'Conf (1-5)':<12} {'Hours':<10} {'Sessions':<10} {'Urgency'}")
    print("-" * 75)
    for a in allocations:
        days_str = f" ({a['days_until_exam']}d)" if a["days_until_exam"] else ""
        print(f"{a['name']:<25} {a['confidence']:<12} {a['allocated_hours']:<10.1f} {a['sessions_per_week']:<10} {a['urgency']}{days_str}")

    print("\n=== RECOMMENDED SPACED REPETITION REVIEW CADENCE ===")
    intervals = compute_spaced_repetition(14)
    for day_offset in intervals:
        review_date = start_dt + timedelta(days=day_offset)
        print(f"Day {day_offset:<2} ({review_date.strftime('%a %Y-%m-%d')}): Review active recall flashcards / summary cheat-sheet")

    print(
        "\nWhat to do next: Use these hour allocations to build the daily checklist table in SKILL.md."
    )


if __name__ == "__main__":
    main()
