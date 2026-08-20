"""
Turns a markdown runbook into overlapping chunks small enough to embed
and retrieve individually, while keeping each chunk's section heading
attached so retrieved text stays understandable out of context.

This is intentionally simple (split on markdown headers, then re-split
long sections by size) rather than pulling in a heavyweight chunking
library. For an interview: this is the kind of design decision you
should be ready to defend — e.g. "why not just split every N
characters?" (Answer: splitting mid-sentence or mid-list breaks the
semantic unit the embedding is supposed to represent, which hurts
retrieval quality.)
"""

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str
    heading: str
    chunk_index: int


def _split_by_headers(markdown_text: str) -> list[tuple[str, str]]:
    """Split a markdown doc into (heading, body) sections on '##' headers."""
    sections = []
    current_heading = "Overview"
    current_lines: list[str] = []

    for line in markdown_text.splitlines():
        header_match = re.match(r"^#{1,6}\s+(.*)", line)
        if header_match:
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = header_match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    return [(h, b) for h, b in sections if b]


def _split_long_section(body: str, max_chars: int, overlap_chars: int) -> list[str]:
    """Further split an over-long section on paragraph boundaries, with overlap."""
    if len(body) <= max_chars:
        return [body]

    paragraphs = [p for p in body.split("\n\n") if p.strip()]
    pieces: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                pieces.append(current)
            # carry a small overlap forward so context isn't lost at the boundary
            overlap = current[-overlap_chars:] if current else ""
            current = f"{overlap}\n\n{para}" if overlap else para

    if current:
        pieces.append(current)

    return pieces


def chunk_document(markdown_text: str, source: str, max_chars: int = 800, overlap_chars: int = 150) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0
    for heading, body in _split_by_headers(markdown_text):
        for piece in _split_long_section(body, max_chars, overlap_chars):
            # Prepend the heading so a retrieved chunk is self-describing even
            # when shown to the LLM out of its original document order.
            text = f"## {heading}\n{piece}"
            chunks.append(Chunk(text=text, source=source, heading=heading, chunk_index=idx))
            idx += 1
    return chunks
