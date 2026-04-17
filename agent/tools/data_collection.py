"""
data_collection.py - State-safe tool for persistent caller data collection.
"""
from typing import Annotated, Optional, Callable, Any
from livekit.agents import function_tool
import logging

logger = logging.getLogger("data-collection")


def create_save_caller_data_tool(lifecycle_manager) -> Callable[..., Any]:
    @function_tool(
        name="save_caller_data",
        description="Save collected caller information like name, phone, or email. Call this as soon as you learn any details.",
    )
    async def save_caller_data(
        full_name: Annotated[Optional[str], "Caller's full name"] = None,
        phone_number: Annotated[Optional[str], "Caller's phone number"] = None,
        email: Annotated[Optional[str], "Caller's email address"] = None,
        inquiry_type: Annotated[Optional[str], "Type of inquiry or reason for calling"] = None,
    ) -> str:
        updates = {
            k: v
            for k, v in {
                "full_name": full_name,
                "phone_number": phone_number,
                "email": email,
                "inquiry_type": inquiry_type,
            }.items()
            if v is not None
        }

        if not updates:
            return "No data provided to save."

        lifecycle_manager.update_caller_data(**updates)
        return f"Saved data: {', '.join(f'{k}={v}' for k, v in updates.items())}. Continue naturally."

    return save_caller_data
