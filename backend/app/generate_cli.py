"""Generate questions for one topic/difficulty and save validated, deduplicated results
to the bank.

Usage:
    python -m app.generate_cli --topic Python --difficulty basic --count 10
    python -m app.generate_cli --topic Python --difficulty basic --count 10 --type scenario
"""

import argparse
import logging

from app.db import get_session, init_db
from app.llm.client import OllamaClient
from app.pipeline import generate_and_save_mcq_batch, generate_and_save_scenario_batch

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--difficulty", required=True, choices=["basic", "mid"])
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--type", choices=["mcq", "scenario"], default="mcq")
    args = parser.parse_args()

    init_db()
    client = OllamaClient()
    session = get_session()

    if args.type == "mcq":
        stats = generate_and_save_mcq_batch(
            client, session, args.topic, args.difficulty, args.count
        )
    else:
        stats = generate_and_save_scenario_batch(
            client, session, args.topic, args.difficulty, args.count
        )

    for q in stats.saved_questions:
        print(f"saved: {q.question_text[:80]}")

    session.close()
    print(
        f"\nDone. requested={args.count} saved={stats.saved} "
        f"skipped_invalid={stats.skipped_invalid} skipped_duplicate={stats.skipped_duplicate}"
    )


if __name__ == "__main__":
    main()
