
import os
import re
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv


load_dotenv()

DEFAULT_VOICE = "en-US-AnaNeural"


def remove_citations(text: str) -> str:
    """Remove citation markers before speaking."""
    return re.sub(r"\[\d+\]", "", text).strip()


def generate_audio(
    text: str,
    output_file: str = "output/ingenuity_answer.mp3",
    voice: str = DEFAULT_VOICE,
) -> Path:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ["AZURE_SPEECH_KEY"],
        region=os.environ["AZURE_SPEECH_REGION"],
    )

    speech_config.speech_synthesis_voice_name = voice

    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=str(output_path)
    )

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = synthesizer.speak_text_async(
        remove_citations(text)
    ).get()

    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        raise RuntimeError(
            f"Speech synthesis failed: {details.reason}\n"
            f"Details: {details.error_details}"
        )

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(
            f"Unexpected speech result: {result.reason}"
        )

    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError("Audio file is missing or empty.")

    return output_path


if __name__ == "__main__":
    sample = (
        "Hello! I'm Ingenuity, NASA's Mars helicopter. "
        "I completed 72 flights on Mars!"
    )

    path = generate_audio(sample)
    print(f"PASS: Audio generated at {path.resolve()}")
