"""
models.py — Data models for call records and caller information.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

class CallOutcome(str, Enum):
    BOOKING = "booking"
    INQUIRY = "inquiry"
    CALLBACK = "callback"
    OTHER = "other"

class CallerData(BaseModel):
    """Structured data collected during the call."""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    inquiry_type: Optional[str] = None
    preferred_contact_time: Optional[str] = None
    custom_fields: dict = Field(default_factory=dict)

class BookingRecord(BaseModel):
    """Details of a booked appointment."""
    event_id: str
    appointment_date: str
    appointment_time: str
    appointment_type: str

class CallRecord(BaseModel):
    """Complete record of a single call."""
    call_id: str
    room_name: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    outcome: CallOutcome = CallOutcome.OTHER
    summary: Optional[str] = None
    caller_data: CallerData = Field(default_factory=CallerData)
    booking: Optional[BookingRecord] = None
    transcript: list[dict] = Field(default_factory=list)
