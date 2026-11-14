
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import ChatRequest, ChatResponse

from scripts.explorer_config import EXPLORERS

import logging

from fastapi import HTTPException
from app.services.rag_service import RagService

import base64
import re

from scripts.test_speech import generate_audio
import os
import tempfile


app = FastAPI(
    title="Space Buddies API",
    description="NASA explorer storytelling powered by RAG.",
    version="1.0.0",
)

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

logger = logging.getLogger(__name__)
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
def chat(request: ChatRequest):
    explorer = EXPLORERS[request.explorer_id]

    try:
        # Retrieve NASA evidence
        chunks = rag_service.retrieve(
            explorer_id=request.explorer_id,
            question=request.question,
        )

        # Generate a grounded answer
        answer = rag_service.generate_answer(
            explorer_id=request.explorer_id,
            question=request.question,
            chunks=chunks,
        )


        # Generate spoken answer using the explorer's voice
        
        audio_base64 = None
        audio_error = None

        temporary_audio_path = None

        try:
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



        # Return the sources used as model context
        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "title": chunk["source_title"],
                "url": chunk["source_url"],
            }
            for chunk in chunks
        ]

        return ChatResponse(
            explorer_id=request.explorer_id,
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

