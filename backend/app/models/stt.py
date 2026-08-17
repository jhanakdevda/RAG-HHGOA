"""
Pydantic Data Models for Speech-To-Text (STT) Transcription
"""

from typing import Optional
from pydantic import BaseModel, Field


class TranscribeResponse(BaseModel):
    """Data model representing the result of Sarvam Speech-to-Text transcription."""
    transcript: str = Field(..., description="Transcribed text string in target or auto-detected language")
    language_code: str = Field(default="en-IN", description="Language code used or detected for STT")
    stt_latency_ms: float = Field(..., description="Latency of Speech-to-Text processing in milliseconds")
    success: bool = Field(default=True, description="Success status of STT transcription")
    error_message: Optional[str] = Field(default=None, description="Detailed error message if transcription failed")
