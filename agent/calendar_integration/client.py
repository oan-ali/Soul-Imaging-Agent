"""
client.py — Cal.com API V2 Client.
Handles slot availability checks and booking creation.
"""
import logging
import httpx
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from agent.config import settings

logger = logging.getLogger("calcom-client")

CALCOM_BASE_URL = "https://api.cal.com/v2"


class CalComClient:
    def __init__(self):
        self.api_key = settings.CALCOM_API_KEY
        self.event_type_id = settings.CALCOM_EVENT_TYPE_ID
        self.timezone = settings.TIMEZONE
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "cal-api-version": "2024-08-13",
            "Content-Type": "application/json",
        }

    async def get_available_slots(
        self, start_date: str, end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch available slots for the configured event type.
        start_date / end_date must be 'YYYY-MM-DD'.
        Returns a list of dicts with 'time' (ISO) and 'display_time' (human).
        """
        if not end_date:
            start_dt = date.fromisoformat(start_date)
            end_date = (start_dt + timedelta(days=7)).isoformat()

        url = f"{CALCOM_BASE_URL}/slots/available"
        params = {
            "eventTypeId": self.event_type_id,
            "startTime": f"{start_date}T00:00:00.000Z",
            "endTime": f"{end_date}T23:59:59.999Z",
            "timeZone": self.timezone,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                # Cal.com v2 response: {"status":"success","data":{"slots":{"2024-05-13":[{"time":"..."},...]}}}
                slots_by_day: Dict[str, List] = data.get("data", {}).get("slots", {})

                formatted_slots = []
                for day_slots in slots_by_day.values():
                    for slot in day_slots:
                        # Each slot is {"time": "2024-05-13T09:00:00.000Z"}
                        time_str = slot.get("time", "") if isinstance(slot, dict) else slot
                        if not time_str:
                            continue
                        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        # Use %I and strip leading zero manually — cross-platform (Windows + Linux)
                        hour_str = dt.strftime("%I").lstrip("0") or "12"
                        display = dt.strftime(f"%A, %B %d at {hour_str}:%M %p")
                        formatted_slots.append(
                            {
                                "time": time_str,  # ISO — passed back to book_appointment
                                "display_time": display,
                                "date": dt.strftime("%Y-%m-%d"),
                            }
                        )

                return formatted_slots

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Cal.com slots HTTP error {e.response.status_code}: {e.response.text}"
                )
                return []
            except Exception as e:
                logger.error(f"Unexpected error fetching Cal.com slots: {e}")
                return []

    async def create_booking(
        self,
        start_time: str,
        name: str,
        email: str,
        phone: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Create a confirmed booking.
        start_time must be the ISO string returned from get_available_slots.
        """
        url = f"{CALCOM_BASE_URL}/bookings"
        payload = {
            "start": start_time,
            "eventTypeId": int(self.event_type_id),
            "attendee": {
                "name": name,
                "email": email,
                "timeZone": self.timezone,
                "language": "en",
            },
            "metadata": {
                "bookedBy": "SarahVoiceAgent",
                "phone": phone,
                "notes": notes,
            },
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return {"status": "success", "data": response.json()}
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Cal.com booking HTTP error {e.response.status_code}: {e.response.text}"
                )
                return {"status": "error", "message": e.response.text}
            except Exception as e:
                logger.error(f"Unexpected error creating Cal.com booking: {e}")
                return {"status": "error", "message": str(e)}


# Module-level singleton
calcom_client = CalComClient()
