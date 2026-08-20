"""
Regression testing for the agent. This is the piece most self-taught AI
projects skip entirely, and it's exactly what separates "I built a demo"
from "I built something I can reason about changing later."

Two layers, on purpose:

1. Deterministic checks (always run, free, fast): did the agent call the
   tools we expected, and does the final answer contain the keywords we
   know a correct answer must contain? This is cheap enough to run on
   every change and catches obvious regressions (e.g. you changed a
   prompt and the agent stopped calling search_runbooks at all).

2. LLM-as-judge (optional, costs a little money, run before anything you
   actually care about): ask a model to rate the answer's accuracy and
   groundedness against the retrieved context on a 1-5 scale. This catches
   subtler regressions the keyword check can't -- e.g. the agent used the
   right tools and said plausible-sounding things, but actually
   contradicted the runbook it retrieved.

    python eval/run_eval.py            # deterministic checks only
    python eval/run_eval.py --judge    # also run the LLM judge pass
"""

import argparse
import asyncio
import json
import os
import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from app.agent import run_agent  # noqa: E402
from app.llm_client import LLMClient  # noqa: E402

JUDGE_PROMPT = """You are grading an AI security assistant's answer for accuracy and groundedness.

Question asked: {question}

Runbook context the assistant retrieved (via tool calls): {context}

Assistant's final answer: {answer}

Rate the answer from 1-5:
5 = fully correct, directly supported by the retrieved context, nothing invented
3 = partially correct, or correct but missing something important from the context
1 = wrong, contradicts the context, or invents information not present in it

Respond with ONLY a single digit 1-5, nothing else.
"""


def deterministic_check(case: dict, answer: str, tool_calls: list[dict]) -> dict:
    called_tool_names = {tc["name"] for tc in tool_calls}
    expected_tools = set(case["expected_tools"])
    tools_ok = expected_tools.issubset(called_tool_names)

    answer_lower = answer.lower()
    missing_keywords = [kw for kw in case["required_keywords"] if kw.lower() not in answer_lower]
    keywords_ok = not missing_keywords

    return {
        "tools_ok": tools_ok,
        "missing_tools": sorted(expected_tools - called_tool_names),
        "keywords_ok": keywords_ok,
        "missing_keywords": missing_keywords,
        "passed": tools_ok and keywords_ok,
    }


async def judge_check(client: LLMClient, case: dict, answer: str, tool_calls: list[dict]) -> int | None:
    context = json.dumps([tc["result"] for tc in tool_calls])[:4000]
    prompt = JUDGE_PROMPT.format(question=case["question"], context=context, answer=answer)
    response = await client.call(system_prompt="You are a strict, careful grader.", messages=[{"role": "user", "content": prompt}], tool_schemas=[])
    text = (response.text or "").strip()
    try:
        return int(text[0])
    except (ValueError, IndexError):
        return None


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", action="store_true", help="also run the LLM-as-judge scoring pass")
    args = parser.parse_args()

    golden_set_path = os.path.join(os.path.dirname(__file__), "golden_set.json")
    with open(golden_set_path) as f:
        cases = json.load(f)

    persist_dir = os.environ.get("CHROMA_DB_DIR", "./chroma_db")
    judge_client = LLMClient() if args.judge else None

    results = []
    for case in cases:
        result = await run_agent(case["question"], persist_dir=persist_dir)
        det = deterministic_check(case, result.answer, result.trace.tool_calls)

        judge_score = None
        if args.judge:
            judge_score = await judge_check(judge_client, case, result.answer, result.trace.tool_calls)

        results.append({"case": case, "answer": result.answer, "deterministic": det, "judge_score": judge_score})

        status = "PASS" if det["passed"] else "FAIL"
        print(f"[{status}] {case['id']}")
        if not det["passed"]:
            if det["missing_tools"]:
                print(f"    missing expected tool calls: {det['missing_tools']}")
            if det["missing_keywords"]:
                print(f"    missing expected keywords: {det['missing_keywords']}")
        if judge_score is not None:
            print(f"    judge score: {judge_score}/5")

    passed = sum(1 for r in results if r["deterministic"]["passed"])
    print(f"\n{passed}/{len(results)} deterministic checks passed")
    if args.judge:
        scored = [r["judge_score"] for r in results if r["judge_score"] is not None]
        if scored:
            print(f"average judge score: {sum(scored) / len(scored):.2f}/5")

    with open(os.path.join(os.path.dirname(__file__), "last_run_results.json"), "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
