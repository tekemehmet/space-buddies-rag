
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_explorers():
    response = client.get("/api/explorers")

    assert response.status_code == 200

    explorers = response.json()

    assert len(explorers) == 6
    assert any(
        explorer["id"] == "ingenuity"
        for explorer in explorers
    )


def test_invalid_explorer():
    response = client.post(
        "/api/chat",
        json={
            "explorer_id": "unknown",
            "question": "What did you discover?",
        },
    )

    assert response.status_code == 422


def test_empty_question():
    response = client.post(
        "/api/chat",
        json={
            "explorer_id": "ingenuity",
            "question": "",
        },
    )

    assert response.status_code == 422


def test_chat_success():
    mock_chunks = [
        {
            "chunk_id": "ingenuity-final-flight-chunk-001",
            "explorer_id": "ingenuity",
            "content": "Ingenuity's rotor blades were damaged.",
            "topic": "final_flight",
            "source_title": "NASA Ingenuity",
            "source_url": "https://www.nasa.gov/",
        }
    ]

    with (
        patch(
            "app.main.rag_service.retrieve",
            return_value=mock_chunks,
        ),
        patch(
            "app.main.rag_service.generate_answer",
            return_value="My rotor blades were damaged [1].",
        ),
        patch(
            "app.main.generate_audio",
        ) as mock_audio,
    ):
        def write_fake_audio(text, voice, output_file):
            with open(output_file, "wb") as audio_file:
                audio_file.write(b"fake-mp3-data")

            return output_file

        mock_audio.side_effect = write_fake_audio

        response = client.post(
            "/api/chat",
            json={
                "explorer_id": "ingenuity",
                "question": "Why did you stop flying?",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["explorer_id"] == "ingenuity"
    assert data["explorer_name"] == "Ingenuity"
    assert data["answer"] == "My rotor blades were damaged [1]."
    assert len(data["sources"]) == 1
    assert data["audio_base64"] is not None
    assert data["audio_error"] is None



def test_chat_rate_limit():
    from fastapi.testclient import TestClient
    from app.main import app, limiter

    # Use a dedicated client IP to isolate this test.
    test_ip = "192.0.2.50"

    # Clear the in-memory limiter state before testing.
    limiter.reset()

    with TestClient(app, client=(test_ip, 50000)) as test_client:
        # Mock all paid Azure operations.
        with (
            patch(
                "app.main.rag_service.retrieve",
                return_value=[],
            ),
            patch(
                "app.main.rag_service.generate_answer",
                return_value="Hello from Mars!",
            ),
            patch(
                "app.main.generate_audio",
            ) as mock_audio,
        ):
            def write_fake_audio(text, voice, output_file):
                with open(output_file, "wb") as audio_file:
                    audio_file.write(b"fake-mp3-data")

                return output_file

            mock_audio.side_effect = write_fake_audio

            payload = {
                "explorer_id": "ingenuity",
                "question": "What was your mission on Mars?",
            }

            # First five requests should succeed.
            for _ in range(5):
                response = test_client.post(
                    "/api/chat",
                    json=payload,
                )
                assert response.status_code == 200

            # The sixth request should be rejected.
            response = test_client.post(
                "/api/chat",
                json=payload,
            )

            assert response.status_code == 429

            # The rejected request must not call Azure services.
            assert mock_audio.call_count == 5

    limiter.reset()
