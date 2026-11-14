
from typing import Literal

from pydantic import BaseModel, Field


ExplorerId = Literal[
    "opportunity",
    "spirit",
    "insight",
    "ingenuity",
    "lunar-module",
    "lunar-rover",
]


class ChatRequest(BaseModel):
    explorer_id: ExplorerId
    question: str = Field(
        min_length=3,
        max_length=1000,
        description="Student's question about the selected NASA explorer.",
    )


class SourceReference(BaseModel):
    chunk_id: str
    title: str
    url: str


class ChatResponse(BaseModel):
    explorer_id: ExplorerId
    explorer_name: str
    answer: str
    sources: list[SourceReference]
    audio_base64: str | None = None
    audio_error: str | None = None
