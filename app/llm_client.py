"""
A thin, provider-agnostic wrapper around the OpenAI and Anthropic tool-use
APIs. This is the piece worth understanding deeply for interviews: both
providers do the same fundamental thing (send messages + tool schemas,
model replies with either a text answer or a request to call a tool, you
run the tool and send the result back, repeat), but the request/response
shapes differ enough that a real agent needs an adapter layer if it's
going to support more than one provider. That's exactly what this is.
"""

import os
from dataclasses import dataclass


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    # Either text is set (model produced a final answer) or tool_calls is
    # non-empty (model wants to call one or more tools before answering).
    text: str | None
    tool_calls: list[ToolCall]
    raw_assistant_message: dict  # provider-native message, needed to build the next turn


class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider = provider or os.environ.get("LLM_PROVIDER", "openai")
        if self.provider == "openai":
            from openai import AsyncOpenAI

            base_url = os.environ.get("OPENAI_BASE_URL") or None
            self._client = AsyncOpenAI(base_url=base_url) if base_url else AsyncOpenAI()
            self._model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == "anthropic":
            import anthropic

            self._client = anthropic.AsyncAnthropic()
            self._model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
        else:
            raise ValueError(f"Unknown LLM_PROVIDER '{self.provider}' (expected 'openai' or 'anthropic')")

    async def call(self, system_prompt: str, messages: list[dict], tool_schemas: list[dict]) -> LLMResponse:
        if self.provider == "openai":
            return await self._call_openai(system_prompt, messages, tool_schemas)
        return await self._call_anthropic(system_prompt, messages, tool_schemas)

    # ---- OpenAI ----
    def _to_openai_tools(self, tool_schemas: list[dict]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tool_schemas
        ]

    async def _call_openai(self, system_prompt: str, messages: list[dict], tool_schemas: list[dict]) -> LLMResponse:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=full_messages,
            tools=self._to_openai_tools(tool_schemas),
        )
        choice = response.choices[0].message
        tool_calls = [
            ToolCall(id=tc.id, name=tc.function.name, input=_safe_json(tc.function.arguments))
            for tc in (choice.tool_calls or [])
        ]
        # Groq rejects extra OpenAI fields like 'annotations' or 'function_call', so we build
        # a clean assistant message manually instead of using choice.model_dump(exclude_unset=True)
        assistant_msg = {"role": "assistant"}
        if choice.content:
            assistant_msg["content"] = choice.content
        if choice.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in choice.tool_calls
            ]

        return LLMResponse(
            text=choice.content if not tool_calls else None,
            tool_calls=tool_calls,
            raw_assistant_message=assistant_msg,
        )

    # ---- Anthropic ----
    async def _call_anthropic(self, system_prompt: str, messages: list[dict], tool_schemas: list[dict]) -> LLMResponse:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            tools=tool_schemas,
        )
        tool_calls = [
            ToolCall(id=block.id, name=block.name, input=block.input)
            for block in response.content
            if block.type == "tool_use"
        ]
        text_blocks = [block.text for block in response.content if block.type == "text"]
        return LLMResponse(
            text="\n".join(text_blocks) if text_blocks and not tool_calls else None,
            tool_calls=tool_calls,
            raw_assistant_message={"role": "assistant", "content": [b.model_dump() for b in response.content]},
        )

    # ---- Building the next turn after tool results come back ----
    def build_followup_messages(
        self, prior_messages: list[dict], response: LLMResponse, tool_results: list[tuple[ToolCall, dict]]
    ) -> list[dict]:
        """Given the messages so far, the assistant response that requested
        tool calls, and the results of running those tools, return the
        updated message list ready for the next `call()`. Kept here (not in
        agent.py) because the shape of a "tool result" message is
        provider-specific."""
        import json

        if self.provider == "openai":
            assistant_msg = response.raw_assistant_message
            tool_result_msgs = [
                {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)}
                for call, result in tool_results
            ]
            return prior_messages + [assistant_msg] + tool_result_msgs

        # anthropic
        assistant_msg = response.raw_assistant_message
        tool_result_content = [
            {"type": "tool_result", "tool_use_id": call.id, "content": json.dumps(result)}
            for call, result in tool_results
        ]
        return prior_messages + [assistant_msg, {"role": "user", "content": tool_result_content}]


def _safe_json(s: str) -> dict:
    import json

    try:
        return json.loads(s) if s else {}
    except json.JSONDecodeError:
        return {}
