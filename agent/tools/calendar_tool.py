"""
calendar_tool.py - State-safe tools for appointment scheduling.
"""
from typing import Annotated, Optional, Callable, Any
import datetime
import logging
from livekit.agents import function_tool
from agent.calendar_integration.client import calcom_client

logger = logging.getLogger("calendar-tool")


def create_check_availability_tool() -> Callable[..., Any]:
    @function_tool(
        name="check_availability",
        description="Check available appointment slots at the clinic for a specific date range.",
    )
    async def check_availability(
        date_from: Annotated[Optional[str], "Start date (YYYY-MM-DD). Defaults to today."] = None,
        date_to: Annotated[Optional[str], "End date (YYYY-MM-DD)."] = None,
    ) -> str:
        if not date_from:
            date_from = datetime.date.today().isoformat()

        logger.info(f"Checking availability: {date_from} to {date_to or 'auto'}")
        slots = await calcom_client.get_available_slots(date_from, date_to)

        if not slots:
            return "No available slots found. Ask for a different date range."

        top_slots = slots[:5]
        slot_list = "\n".join(f"- {s['display_time']} (Ref: {s['time']})" for s in top_slots)
        return f"Available slots:\n{slot_list}\n\nOffer 2-3 specific times to the caller."

    return check_availability


def create_book_appointment_tool(lifecycle_manager) -> Callable[..., Any]:
    @function_tool(
        name="book_appointment",
        description="Book a confirmed appointment. Call this ONLY after the caller picks a slot and provides name/email.",
    )
    async def book_appointment(
        start_time: Annotated[str, "The Ref string from check_availability (ISO format)."],
        name: Annotated[str, "Caller's full name."],
        email: Annotated[str, "Caller's email address."],
        phone: Annotated[str, "Caller's phone number."],
        reason: Annotated[Optional[str], "Reason for visit."] = "General Radiology",
    ) -> str:
        logger.info(f"Booking {name} at {start_time}")
        result = await calcom_client.create_booking(
            start_time=start_time,
            name=name,
            email=email,
            phone=phone,
            notes=reason,
        )

        if result.get("status") == "success":
            booking_data = result.get("data", {})
            event_id = str(booking_data.get("id", "booked"))
            lifecycle_manager.record_booking(
                event_id=event_id,
                date=start_time[:10],
                time=start_time[11:16],
                appointment_type=reason,
            )
            return f"Confirmed! Appointment set for {start_time[:10]} at {start_time[11:16]}. Confirmation email sent to {email}."

        return f"Booking failed: {result.get('message', 'Slot may have been taken.')}"

    return book_appointment
