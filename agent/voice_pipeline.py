"""
voice_pipeline.py — Configures the underlying STT, LLM, and TTS plugins for the agent.
"""
import logging
from livekit.plugins import openai as lk_openai
from livekit.plugins import cartesia, gladia, silero
from agent.config import settings

logger = logging.getLogger("voice-pipeline")

def get_stt():
    logger.info("Initializing Gladia STT (English only)...")
    return gladia.STT(
        languages=["en"],
        code_switching=False,
    )

def get_llm():
    # Force use of a real OpenAI model instead of the fake one from the .env file.
    model_name = settings.OPENAI_MODEL
    if "gpt-5" in model_name or "nano" in model_name:
        model_name = "gpt-4o-mini"
        logger.warning(f"Invalid model {settings.OPENAI_MODEL} requested, falling back to {model_name}")

    return lk_openai.LLM(
        model=model_name or "gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.3,
        parallel_tool_calls=False, # Reduces TTFT significantly
    )


def get_tts(voice_id: str = None):
    logger.info("Initializing Cartesia TTS...")
    return cartesia.TTS(
        api_key=settings.CARTESIA_API_KEY,
        voice=voice_id or settings.CARTESIA_VOICE_ID,
    )

def get_vad():
    return silero.VAD.load(
        min_silence_duration=0.4,
        activation_threshold=0.5,
    )

