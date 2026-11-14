
import base64
import logging
import os
import re
import tempfile

from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.schemas import ChatRequest, ChatResponse
from app.services.rag_service import RagService
from scripts.explorer_config import EXPLORERS
from scripts.test_speech import generate_audio
from fastapi import FastAPI, HTTPException, Request, Response


logger = logging.getLogger(__name__)

# Rate limiting:
# Use the connection's remote address rather than trusting
# arbitrary X-Forwarded-For headers supplied by clients.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    headers_enabled=True,
)

app = FastAPI(
    title="Space Buddies API",
    description="NASA explorer storytelling powered by RAG.",
    version="1.0.0",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded,
):
    from slowapi import _rate_limit_exceeded_handler

    return _rate_limit_exceeded_handler(request, exc)


app.add_middleware(SlowAPIMiddleware)

# Local development frontend only.
# Production frontend origins will be configured later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

rag_service = RagService()


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "space-buddies-api",
    }


@app.get("/api/explorers")
def list_explorers():
    return [
        {
            "id": explorer_id,
            "name": config["name"],
            "description": config["description"],
        }
        for explorer_id, config in EXPLORERS.items()
    ]


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
def chat(request: Request, payload: ChatRequest,response: Response,):
    explorer = EXPLORERS[payload.explorer_id]

    try:
        # Retrieve NASA evidence.
        chunks = rag_service.retrieve(
            explorer_id=payload.explorer_id,
            question=payload.question,
        )

        # Generate a grounded answer.
        answer = rag_service.generate_answer(
            explorer_id=payload.explorer_id,
            question=payload.question,
            chunks=chunks,
        )

        audio_base64 = None
        audio_error = None
        temporary_audio_path = None

        try:
            # Remove citation markers before narration.
            spoken_text = re.sub(
                r"\[\d+\]",
                "",
                answer,
            ).strip()

            # Create a unique temporary file per request.
            with tempfile.NamedTemporaryFile(
                suffix=".mp3",
                delete=False,
            ) as temp_file:
                temporary_audio_path = temp_file.name

            generate_audio(
                text=spoken_text,
                voice=explorer["voice"],
                output_file=temporary_audio_path,
            )

            with open(temporary_audio_path, "rb") as audio_file:
                audio_base64 = base64.b64encode(
                    audio_file.read()
                ).decode("utf-8")

        except Exception:
            logger.exception("Speech synthesis failed")
            audio_error = "Audio is temporarily unavailable."

        finally:
            if temporary_audio_path and os.path.exists(
                temporary_audio_path
            ):
                os.remove(temporary_audio_path)

        # Return NASA sources used as model context.
        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "title": chunk["source_title"],
                "url": chunk["source_url"],
            }
            for chunk in chunks
        ]

        return ChatResponse(
            explorer_id=payload.explorer_id,
            explorer_name=explorer["name"],
            answer=answer,
            sources=sources,
            audio_base64=audio_base64,
            audio_error=audio_error,
        )

    except Exception:
        logger.exception("RAG request failed")

        raise HTTPException(
            status_code=503,
            detail="The NASA knowledge service is temporarily unavailable.",
        )
