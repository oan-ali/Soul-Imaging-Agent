"""
tests/test_components.py — Component-level integration tests.
Run: python -m tests.test_components
Tests each API (Cal.com, Supabase, Knowledge Base, OpenAI Embeddings).
"""
import asyncio
import os
import sys
import json
import datetime

# Ensure we load .env before any agent imports
from dotenv import load_dotenv
load_dotenv()

from agent.config import settings


async def test_config():
    """Verify all required environment variables are set."""
    print("\n[1/4] Testing configuration...")
    required = [
        "LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY", "GLADIA_API_KEY",
        "CARTESIA_API_KEY", "CARTESIA_VOICE_ID",
        "CALCOM_API_KEY", "CALCOM_EVENT_TYPE_ID",
        "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY",
    ]
    missing = []
    for key in required:
        val = getattr(settings, key, None)
        if not val or val.startswith("your_") or val == "":
            missing.append(key)
        else:
            print(f"  OK  {key} = {val[:20]}...")

    if missing:
        print(f"  FAIL Missing: {missing}")
        return False
    print("  Config OK")
    return True


async def test_knowledge_base():
    """Test knowledge base loading and search."""
    print("\n[2/4] Testing knowledge base...")
    try:
        from agent.knowledge.loader import ingest_knowledge_base
        from agent.knowledge.store import knowledge_store

        await ingest_knowledge_base()

        if not knowledge_store._is_loaded:
            print("  FAIL Knowledge base failed to load")
            return False

        print(f"  Loaded {len(knowledge_store.chunks)} chunks")

        result = await knowledge_store.search("What are your opening hours?", top_k=1)
        if result and "I'm sorry" not in result and "Internal error" not in result:
            print(f"  Search result (truncated): {result[:120]}...")
            print("  Knowledge base OK")
            return True
        else:
            print(f"  FAIL Bad search result: {result}")
            return False

    except Exception as e:
        print(f"  FAIL {type(e).__name__}: {e}")
        return False


async def test_calcom():
    """Test Cal.com slot fetching."""
    print("\n[3/4] Testing Cal.com API...")
    try:
        from agent.calendar_integration.client import calcom_client

        today = datetime.date.today().isoformat()
        slots = await calcom_client.get_available_slots(today)

        if slots is None:
            print("  FAIL slots returned None")
            return False

        if len(slots) == 0:
            print("  WARN No slots found for next 7 days (may be correct if calendar is empty)")
            print("  Cal.com API responded OK (empty schedule)")
            return True

        print(f"  Found {len(slots)} available slots")
        print(f"  First slot: {slots[0]['display_time']}")
        print("  Cal.com OK")
        return True

    except Exception as e:
        print(f"  FAIL {type(e).__name__}: {e}")
        return False


async def test_supabase():
    """Test Supabase write (inserts a test record then deletes it)."""
    print("\n[4/4] Testing Supabase connection...")
    try:
        import httpx
        import uuid

        test_id = str(uuid.uuid4())
        url = f"{settings.SUPABASE_URL}/rest/v1/call_logs"
        headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        payload = {
            "call_id": test_id,
            "room_name": "test-room",
            "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "outcome": "other",
            "transcript": [],
            "caller_data": {},
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Insert
            r = await client.post(url, json=payload, headers=headers)
            if r.status_code not in (200, 201):
                print(f"  FAIL Insert returned {r.status_code}: {r.text[:200]}")
                return False
            print(f"  Insert OK (status {r.status_code})")

            # Delete the test row
            del_url = f"{url}?call_id=eq.{test_id}"
            r2 = await client.delete(del_url, headers={**headers, "Prefer": "return=minimal"})
            print(f"  Cleanup OK (status {r2.status_code})")

        print("  Supabase OK")
        return True

    except Exception as e:
        print(f"  FAIL {type(e).__name__}: {e}")
        return False


async def main():
    print("=" * 50)
    print(" Soul Imaging Voice Agent — Component Tests")
    print("=" * 50)

    results = {
        "Config":          await test_config(),
        "Knowledge Base":  await test_knowledge_base(),
        "Cal.com":         await test_calcom(),
        "Supabase":        await test_supabase(),
    }

    print("\n" + "=" * 50)
    print(" RESULTS")
    print("=" * 50)
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print(" ALL TESTS PASSED - Agent is ready")
    else:
        print(" SOME TESTS FAILED - Fix issues above before deploying")
    print("=" * 50)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
