"""
config.py — Configuration management using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # LiveKit
    LIVEKIT_URL: str
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Gladia
    GLADIA_API_KEY: str

    # Cartesia
    CARTESIA_API_KEY: str
    CARTESIA_VOICE_ID: str

    # Cal.com
    CALCOM_API_KEY: str
    CALCOM_EVENT_TYPE_ID: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Clinic Identity
    CLINIC_NAME: str = "Soul Imaging Radiology Clinic"
    AGENT_NAME: str = "Sarah"
    TIMEZONE: str = "Australia/Sydney"
    API_ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
