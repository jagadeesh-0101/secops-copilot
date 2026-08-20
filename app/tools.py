"""
The tools the agent is allowed to call. Each tool is a plain Python
function plus a JSON-schema description of its inputs — that schema is
what actually gets sent to the LLM so it knows the tool exists and how
to call it correctly.

Kept to three tools on purpose. A common mistake in agent demos is
bolting on ten tools "for coverage" — in an interview you want to be
able to explain exactly why each tool exists and what would break
without it, which gets harder the more you add.
"""

import os

from pydantic import BaseModel, ValidationError

from app.retriever import search

# Resolve the project root from this file's location so that paths work
# regardless of the process's current working directory.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS_DIR = os.environ.get("SECOPS_DOCS_DIR", os.path.join(_PROJECT_ROOT, "sample_docs"))

# A tiny, static "threat intel" blocklist standing in for a real feed
# (VirusTotal, AbuseIPDB, etc). Swappable for a real API call later —
# the point right now is the tool-calling contract, not the data source.
_KNOWN_BAD_INDICATORS = {
    "185.220.101.7": "Known Tor exit node associated with credential-phishing infrastructure.",
    "malicious-update-portal.com": "Registered 4 days ago; flagged in three independent phishing campaigns this month.",
    "secure-login-verify.net": "Typosquat domain impersonating a common SSO provider.",
}

TOOL_SCHEMAS = [
    {
        "name": "search_runbooks",
        "description": (
            "Semantic search over the security team's internal runbooks and policies. "
            "Use this whenever the user asks what the correct procedure, SLA, or "
            "escalation path is for a security situation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A natural-language description of the situation or question.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "check_indicator",
        "description": (
            "Check whether a domain or IP address is a known-bad indicator of compromise "
            "against internal threat intelligence. Use this when an incident involves a "
            "specific domain, URL, or IP address."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "indicator": {
                    "type": "string",
                    "description": "The domain name or IP address to check.",
                }
            },
            "required": ["indicator"],
        },
    },
    {
        "name": "classify_severity",
        "description": (
            "Given a short factual description of what happened in an incident, return the "
            "severity tier definitions from policy so the agent can reason about which tier "
            "applies. This does NOT make the judgment call itself — it returns the criteria "
            "so the LLM reasons over them explicitly and can show its work."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "incident_type": {
                    "type": "string",
                    "enum": ["phishing", "dlp", "vulnerability", "general_escalation"],
                    "description": "Which severity rubric to retrieve.",
                }
            },
            "required": ["incident_type"],
        },
    },
]

_SEVERITY_DOC_MAP = {
    "phishing": "phishing_response_runbook.md",
    "dlp": "dlp_incident_handling.md",
    "vulnerability": "vulnerability_management.md",
    "general_escalation": "incident_escalation_policy.md",
}


# ---- Pydantic models for tool input validation ----

class SearchRunbooksInput(BaseModel):
    query: str


class CheckIndicatorInput(BaseModel):
    indicator: str


class ClassifySeverityInput(BaseModel):
    incident_type: str


def search_runbooks(query: str, persist_dir: str, top_k: int = 4) -> dict:
    hits = search(query, persist_dir=persist_dir, top_k=top_k)
    return {
        "hits": [
            {"source": h["source"], "heading": h["heading"], "text": h["text"], "similarity": h["similarity"]}
            for h in hits
        ]
    }


def check_indicator(indicator: str) -> dict:
    indicator = indicator.strip().lower()
    match = _KNOWN_BAD_INDICATORS.get(indicator)
    if match:
        return {"indicator": indicator, "known_malicious": True, "detail": match}
    return {
        "indicator": indicator,
        "known_malicious": False,
        "detail": "No match in internal threat intel. This does not confirm the indicator is safe, only that it isn't already known-bad.",
    }


def classify_severity(incident_type: str, persist_dir: str) -> dict:
    doc_name = _SEVERITY_DOC_MAP.get(incident_type)
    if not doc_name:
        return {"error": f"Unknown incident_type '{incident_type}'"}
    # Pull the "Severity" section directly rather than doing a fuzzy search —
    # we know exactly which document and section we want here.
    path = os.path.join(_DOCS_DIR, doc_name)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"source": doc_name, "full_policy_text": content}


def execute_tool(name: str, tool_input: dict, persist_dir: str) -> dict:
    """Dispatch a tool call by name. Validates inputs with Pydantic before
    calling the tool, so a malformed LLM-generated tool call returns a
    structured error dict instead of crashing the agent loop."""
    try:
        if name == "search_runbooks":
            validated = SearchRunbooksInput(**tool_input)
            return search_runbooks(validated.query, persist_dir=persist_dir)
        if name == "check_indicator":
            validated = CheckIndicatorInput(**tool_input)
            return check_indicator(validated.indicator)
        if name == "classify_severity":
            validated = ClassifySeverityInput(**tool_input)
            return classify_severity(validated.incident_type, persist_dir=persist_dir)
        return {"error": f"Unknown tool '{name}'"}
    except ValidationError as e:
        missing = [str(err["loc"][0]) for err in e.errors() if err["type"] == "missing"]
        if missing:
            return {"error": f"Missing required field(s): {', '.join(repr(f) for f in missing)}"}
        return {"error": f"Invalid tool input: {'; '.join(err['msg'] for err in e.errors())}"}
