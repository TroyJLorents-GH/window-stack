"""Speech-to-text transcription for voice input.

Receives audio from the phone app and transcribes it.
Uses OpenAI Whisper API for reliable transcription.
Falls back to offline Windows Speech Recognition if no API key.
"""

import base64
import io
import os
import tempfile
import wave

# Try to import speech_recognition for offline fallback
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# Try to import openai for Whisper API
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def transcribe_audio(audio_base64: str, format: str = "wav") -> dict:
    """Transcribe base64-encoded audio to text.

    Tries OpenAI Whisper first (if API key set), then falls back to
    offline speech recognition.

    Returns: {"text": "transcribed text", "method": "whisper|offline", "success": bool}
    """
    try:
        # Decode base64 audio to bytes
        audio_bytes = base64.b64decode(audio_base64)

        # Try Whisper API first
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and HAS_OPENAI:
            return _transcribe_whisper(audio_bytes, format, api_key)

        # Fall back to offline recognition
        if HAS_SR:
            return _transcribe_offline(audio_bytes, format)

        return {
            "text": "",
            "method": "none",
            "success": False,
            "error": "No transcription backend available. Install openai or SpeechRecognition.",
        }

    except Exception as e:
        return {"text": "", "method": "error", "success": False, "error": str(e)}


def _transcribe_whisper(audio_bytes: bytes, format: str, api_key: str) -> dict:
    """Transcribe using OpenAI Whisper API."""
    client = OpenAI(api_key=api_key)

    # Write to temp file (Whisper API needs a file)
    suffix = f".{format}"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        temp_path = f.name

    try:
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
            )

        return {"text": transcript.strip(), "method": "whisper", "success": True}
    finally:
        os.unlink(temp_path)


def _transcribe_offline(audio_bytes: bytes, format: str) -> dict:
    """Transcribe using Windows offline speech recognition."""
    recognizer = sr.Recognizer()

    # Write to temp WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        temp_path = f.name

    try:
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)

        # Try Windows Speech API first
        try:
            text = recognizer.recognize_google(audio_data)
            return {"text": text, "method": "google", "success": True}
        except sr.UnknownValueError:
            return {"text": "", "method": "google", "success": False, "error": "Could not understand audio"}
        except sr.RequestError:
            pass

        # If Google fails, try Sphinx (fully offline)
        try:
            text = recognizer.recognize_sphinx(audio_data)
            return {"text": text, "method": "sphinx", "success": True}
        except Exception:
            return {"text": "", "method": "offline", "success": False, "error": "Offline recognition failed"}

    finally:
        os.unlink(temp_path)
