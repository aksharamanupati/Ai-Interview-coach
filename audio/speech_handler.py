"""
Speech recognition (STT) and Text-to-Speech (TTS) handler.
Includes text-fallback and graceful failure recovery.
"""
import io
import logging
from typing import Optional
from gtts import gTTS
import speech_recognition as sr

logger = logging.getLogger(__name__)

def synthesize_speech(text: str) -> Optional[bytes]:
    """Convert text to speech MP3 bytes using gTTS."""
    if not text.strip():
        return None
    try:
        clean_text = text.replace("**", "").replace("*", "")
        fp = io.BytesIO()
        tts = gTTS(text=clean_text[:500], lang="en", slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        logger.warning(f"TTS synthesis warning: {e}")
        return None

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribe audio bytes (WAV/FLAC) to text using SpeechRecognition."""
    if not audio_bytes:
        return ""
    recognizer = sr.Recognizer()
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        logger.warning(f"Speech recognition service request error: {e}")
        return ""
    except Exception as e:
        logger.warning(f"Audio transcription error: {e}")
        return ""
