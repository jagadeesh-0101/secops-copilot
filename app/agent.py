"""
The agent loop: the actual "agentic" part of this project.

At each step, the LLM either produces a final answer, or asks to call one
or more tools. If it asks for tools, we run them, feed the results back
in, and ask again — up to MAX_STEPS times, so a confused model can't loop
forever and burn API credits. This bounded-loop-with-a-trace pattern is
the core thing worth being able to explain in an interview: it's not
magic, it's a while loop with a stop condition and a full audit trail.
"""

import os
from dataclasses import dataclass, field

from app.llm_client import LLMClient
from app.tools import TOOL_SCHEMAS, execute_tool

MAX_STEPS = 5

SYSTEM_PROMPT = """You are SecOps Copilot, an assistant for a security operations team.

Answer questions using ONLY the internal runbooks and tools available to you — do not
rely on general security knowledge that isn't grounded in what the tools return, since
this team's actual procedures may differ from generic best practice.

Always use search_runbooks before answering a "what's the procedure / what's the SLA /
who do I escalate to" question. Use check_indicator when the user mentions a specific
domain or IP. Use classify_severity when you need the exact severity-tier definitions
for a given incident type before making a judgment call.

When you give a final answer:
- Cite which runbook(s) and section(s) it came from.
- If the tools didn't return anything relevant, say so plainly instead of guessing.
- Be concise. This is used during live incidents, not for essay writing.
"""


@dataclass
class AgentTrace:
    tool_calls: list[dict] = field(default_factory=list)
    steps_used: int = 0


@dataclass
class AgentResult:
    answer: str
    trace: AgentTrace


async def run_agent(question: str, persist_dir: str, client: LLMClient | None = None) -> AgentResult:
    client = client or LLMClient()
    trace = AgentTrace()

    messages = [{"role": "user", "content": question}]

    for step in range(MAX_STEPS):
        trace.steps_used = step + 1
        response = await client.call(SYSTEM_PROMPT, messages, TOOL_SCHEMAS)

        if not response.tool_calls:
            return AgentResult(answer=response.text or "(no answer produced)", trace=trace)

        tool_results = []
        for call in response.tool_calls:
            result = execute_tool(call.name, call.input, persist_dir=persist_dir)
            trace.tool_calls.append({"name": call.name, "input": call.input, "result": result})
            tool_results.append((call, result))

        messages = client.build_followup_messages(messages, response, tool_results)

    return AgentResult(
        answer=f"Stopped after {MAX_STEPS} tool-call steps without a final answer — likely stuck in a loop. "
        f"Check the trace for what it was trying to do.",
        trace=trace,
    )
