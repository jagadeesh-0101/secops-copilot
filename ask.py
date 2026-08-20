"""
Quick CLI for talking to the agent without spinning up the API server.
Requires ingest.py to have been run first, and a valid API key in .env.

    python ask.py "a user clicked a link and entered their password, what do I do"
"""

import asyncio
import json
import os
import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

from app.agent import run_agent  # noqa: E402


async def main():
    if len(sys.argv) < 2:
        print('Usage: python ask.py "your question here"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    persist_dir = os.environ.get("CHROMA_DB_DIR", "./chroma_db")

    result = await run_agent(question, persist_dir=persist_dir)

    print("\n=== ANSWER ===")
    print(result.answer)

    print(f"\n=== TRACE ({result.trace.steps_used} step(s), {len(result.trace.tool_calls)} tool call(s)) ===")
    for call in result.trace.tool_calls:
        print(f"- {call['name']}({json.dumps(call['input'])})")


if __name__ == "__main__":
    asyncio.run(main())
