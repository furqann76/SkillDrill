"""Phase 1 vertical slice: generate MCQs for one topic/difficulty and save to the bank.

Usage:
    python -m app.generate_cli --topic Python --difficulty basic --count 10
"""

import argparse
import logging

from app.bank import save_mcq
from app.db import get_session, init_db
from app.llm.client import OllamaClient
from app.llm.mcq_generator import generate_mcq

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--difficulty", required=True, choices=["basic", "mid"])
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    init_db()
    client = OllamaClient()
    session = get_session()

    saved = 0
    skipped = 0
    for i in range(args.count):
        mcq = generate_mcq(client, args.topic, args.difficulty)
        if mcq is None:
            skipped += 1
            continue
        save_mcq(session, args.topic, mcq)
        saved += 1
        print(f"[{i + 1}/{args.count}] saved: {mcq.question_text[:80]}")

    session.close()
    print(f"\nDone. saved={saved} skipped={skipped}")


if __name__ == "__main__":
    main()
