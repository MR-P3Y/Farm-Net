import hashlib
import math
from dataclasses import dataclass


CHUNKER_VERSION = "barzegar-fa-page-v1"


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_index: int
    character_start: int
    character_end: int
    text: str
    text_sha256: str
    token_estimate: int


def chunk_persian_page(
    text: str,
    *,
    max_characters: int = 1200,
    overlap_characters: int = 160,
) -> tuple[KnowledgeChunk, ...]:
    """Create deterministic, page-bounded chunks with stable source offsets."""
    if max_characters < 200:
        raise ValueError("max_characters must be at least 200")
    if overlap_characters < 0 or overlap_characters >= max_characters:
        raise ValueError("overlap_characters must be between 0 and max_characters")
    if not text:
        return ()

    chunks: list[KnowledgeChunk] = []
    start = 0
    while start < len(text):
        hard_end = min(len(text), start + max_characters)
        end = hard_end
        if hard_end < len(text):
            boundary_floor = start + max_characters // 2
            candidates = [
                text.rfind("\n", boundary_floor, hard_end),
                text.rfind(". ", boundary_floor, hard_end),
                text.rfind("؟ ", boundary_floor, hard_end),
                text.rfind("؛ ", boundary_floor, hard_end),
                text.rfind(" ", boundary_floor, hard_end),
            ]
            boundary = max(candidates)
            if boundary > start:
                end = boundary + 1

        chunk_text = text[start:end]
        chunks.append(
            KnowledgeChunk(
                chunk_index=len(chunks),
                character_start=start,
                character_end=end,
                text=chunk_text,
                text_sha256=hashlib.sha256(chunk_text.encode("utf-8")).hexdigest(),
                token_estimate=max(1, math.ceil(len(chunk_text) / 3)),
            )
        )
        if end == len(text):
            break
        start = max(start + 1, end - overlap_characters)

    return tuple(chunks)
