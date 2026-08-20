# SecOps Copilot

A retrieval-augmented, tool-using AI assistant for security operations — built to be
run, understood, and extended

It answers questions like *"a user entered their password on a phishing page, what do
I do?"* by searching a local library of security runbooks, checking indicators of
compromise against a threat-intel lookup, and reasoning step by step about which tool
to call before giving a grounded, cited answer.

## Why this project (and not a generic "chat with your PDFs" clone)

This is deliberately built around a security-operations domain instead of a generic
document type, because it's meant to be a genuine, defensible answer to "tell me about
a project you built" in an interview — not a copy of the first RAG tutorial result.
The five runbooks in `sample_docs/` are written to mirror real SOC workflows (SIEM
alert triage, DLP incident handling, vulnerability management SLAs, phishing response,
incident escalation) — the same kind of process documentation a real security
operations analyst works from daily.

## What it demonstrates (and why each piece is here)

| Skill | Where | Why it's here |
|---|---|---|
| RAG | `app/chunking.py`, `app/retriever.py` | Header-aware chunking (not naive fixed-size splitting) + a local Chroma vector store. Runs offline with zero API cost for embeddings. |
| Tool-calling / agents | `app/tools.py`, `app/agent.py` | A bounded loop (max 5 steps) that lets the model decide which of three tools to call, executes them, and feeds results back in. Full trace of every tool call is kept, not just the final answer. |
| Multi-provider LLM integration | `app/llm_client.py` | One interface, two backends (OpenAI and Anthropic tool-use APIs), because real job postings ask for either — and building the adapter is what actually teaches you how tool-calling works under the hood, instead of only ever seeing it through one SDK. |
| Evaluation | `eval/golden_set.json`, `eval/run_eval.py` | The piece most self-taught AI projects skip. Two layers: free deterministic checks (right tools called? right facts present?) for fast regression testing, plus an optional LLM-as-judge pass for qualitative grading. |
| Deployment | `app/api.py` | A FastAPI wrapper turning the agent into an actual HTTP service. |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then fill in OPENAI_API_KEY or ANTHROPIC_API_KEY
python ingest.py            # builds the local vector store from sample_docs/
```

Ingestion needs no API key — it runs Chroma's local embedding model
(all-MiniLM-L6-v2 via onnxruntime), which downloads once on first run. The LLM step
(the actual agent reasoning and tool-calling) does need a real API key, since that
part has to talk to OpenAI or Anthropic.

## Running this for $0

You do not need a paid OpenAI or Anthropic key to use this project. `.env.example`
has three ready-to-use options, fully documented inline -- uncomment whichever one
you want in your `.env`:

- **Groq's free tier** (recommended if you just want it working fast): sign up at
  console.groq.com with no credit card, generate a key, and point `OPENAI_BASE_URL`
  at Groq's OpenAI-compatible endpoint. Free-tier rate limits are generous enough
  for running the eval suite and normal testing.
- **Ollama** (recommended if you want it fully offline): install Ollama, pull a
  tool-calling-capable model like `qwen2.5:7b`, and point `OPENAI_BASE_URL` at your
  local Ollama server. No signup, no internet needed after the model download,
  no rate limits -- just your own machine's compute.

Both work through the exact same `LLM_PROVIDER=openai` code path in
`app/llm_client.py`, because Groq and Ollama both implement an OpenAI-compatible
`chat.completions` API with tool-calling support -- the only thing that changes is
`OPENAI_BASE_URL`. Nothing else in the project needs to know or care which one
you're using.

One real tradeoff worth knowing: free/local models are noticeably weaker than
GPT-4o-mini or Claude at reliably picking the right tool to call, especially on
ambiguous questions. If you see `eval/run_eval.py` failing cases it wouldn't fail
on a paid model, that's expected -- it's actually a good, honest thing to have
noticed and be able to talk about (model choice is a real production tradeoff
between cost and tool-selection reliability, not just a config value).

## Using it

```bash
# one-off question from the command line
python ask.py "a user entered their password on a phishing page, what do I do"

# or run it as a service
uvicorn app.api:app --reload
curl -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question": "how fast do we need to patch a critical CVE on an internet-facing server"}'
```

## Running the eval suite

```bash
python eval/run_eval.py            # fast, free, deterministic checks
python eval/run_eval.py --judge    # also scores each answer 1-5 with an LLM judge
```

Results are also written to `eval/last_run_results.json` for inspection.

## What I'd genuinely recommend extending next

Don't stop at "it runs" — a few natural next steps that would each teach you something
real and give you more to talk about:

- **Swap in real API embeddings** (OpenAI `text-embedding-3-small`) instead of the
  local model and compare retrieval quality on a few tricky queries. This is a real,
  common production tradeoff (cost/latency vs. quality) worth being able to speak to
  concretely instead of abstractly.
- **Add a fourth tool** that does something you understand from your own SOC
  background — e.g. a mock Splunk query tool. Writing the tool schema and the
  dispatch logic yourself, end to end, is what makes this genuinely yours rather than
  a template you filled in.
- **Add reranking** to the retriever — right now it's a single dense-vector search;
  a lot of production RAG systems add a reranking step after the initial retrieval to
  improve precision on the top few results.
- **Point it at real content.** Swap the sample runbooks for public material you can
  legally use (NIST guides, MITRE ATT&CK summaries) or your own notes from the SOC
  role, so what it answers is something you'd actually stand behind.

## An honest note on how to use this for job applications

Read through every file before you put this on a resume or talk about it in an
interview. The value of this project is that you can explain *why* it's built the way
it is — the chunking strategy, the bounded agent loop, the two-layer eval approach —
not just that it exists. If an interviewer asks "why did you cap the agent loop at 5
steps" or "why two eval layers instead of one," you should be able to answer that in
your own words, because you will get asked exactly that kind of question.
