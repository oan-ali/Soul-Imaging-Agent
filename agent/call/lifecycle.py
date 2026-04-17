"""
lifecycle.py — Manages the state machine of a phone call.
"""
import uuid
import datetime
import logging
from agent.call.models import CallRecord, CallerData, CallOutcome, BookingRecord
from agent.call.summary import generate_call_summary

logger = logging.getLogger("call-lifecycle")

class CallLifecycleManager:
    """Tracks the full lifecycle of a voice call."""

    def __init__(self, room_name: str):
        self.record = CallRecord(
            call_id=str(uuid.uuid4()),
            room_name=room_name,
            started_at=datetime.datetime.now(datetime.timezone.utc),
        )
        logger.info(f"Call started: {self.record.call_id} in room {room_name}")

    def update_caller_data(self, **kwargs):
        """Incrementally update caller data as it's collected."""
        for key, value in kwargs.items():
            if hasattr(self.record.caller_data, key) and value:
                setattr(self.record.caller_data, key, value)
        logger.info(f"Caller data updated: {kwargs}")

    def record_booking(self, event_id: str, date: str, time: str, appointment_type: str):
        """Record a successful booking."""
        self.record.booking = BookingRecord(
            event_id=event_id,
            appointment_date=date,
            appointment_time=time,
            appointment_type=appointment_type,
        )
        self.record.outcome = CallOutcome.BOOKING
        logger.info(f"Booking recorded: {event_id}")

    async def finalize(self, transcript: list[dict]):
        """Called when the call ends. Generates summary and logs everything."""
        self.record.ended_at = datetime.datetime.now(datetime.timezone.utc)
        self.record.duration_seconds = (
            self.record.ended_at - self.record.started_at
        ).total_seconds()
        self.record.transcript = transcript

        # Auto-classify outcome if not already set
        if self.record.outcome == CallOutcome.OTHER:
            self.record.outcome = self._classify_outcome(transcript)

        # Generate AI summary
        try:
            self.record.summary = await generate_call_summary(
                transcript=transcript,
                caller_data=self.record.caller_data
            )
        except Exception as e:
            logger.error(f"Failed to generate call summary: {e}")

        logger.info(f"Call ended: {self.record.call_id}, Duration: {self.record.duration_seconds}s, Outcome: {self.record.outcome}")
        
        # In a real production app, we would save self.record to Supabase here.
        # Let's add that logic.
        await self._save_to_supabase()

        return self.record

    def _classify_outcome(self, transcript: list[dict]) -> CallOutcome:
        """Smarter outcome classification."""
        # 1. If we have a booking record, it's definitely a booking
        if self.record.booking:
            return CallOutcome.BOOKING

        # 2. Key-word based fallback
        full_text = " ".join([str(t.get("content", "")) for t in transcript]).lower()

        if any(word in full_text for word in ["booked", "appointment confirmed", "scheduled", "reservation", "confirmed"]):
            return CallOutcome.BOOKING
        elif any(word in full_text for word in ["call back", "callback", "someone will contact", "call me", "phone number"]):
            return CallOutcome.CALLBACK
        elif any(word in full_text for word in ["question", "wondering", "information", "price", "cost", "where", "how"]):
            return CallOutcome.INQUIRY

        return CallOutcome.OTHER

    async def _save_to_supabase(self):
        """Save the final call record to Supabase."""
        from agent.config import settings
        import httpx
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            return

        url = f"{settings.SUPABASE_URL}/rest/v1/call_logs"
        headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        payload = self.record.model_dump(mode='json')
        
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Saving call {self.record.call_id} to Supabase...")
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code >= 400:
                    logger.error(f"Supabase save failed ({response.status_code}): {response.text}")
                else:
                    logger.info(f"Successfully saved call {self.record.call_id} to Supabase")
            except Exception as e:
                logger.error(f"Network error saving to Supabase: {e}")
