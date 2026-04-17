import logging
import httpx
import json
import time
from agent.config import settings

logger = logging.getLogger("settings-manager")
_CACHE_TTL_SECONDS = 30
import asyncio

_LIVE_CONFIG: dict = {}
_LAST_REFRESH: float = 0


def _coerce_value(value):
    if not isinstance(value, str):
        return value
    v = value.strip()
    if (v.startswith("{") and v.endswith("}")) or (v.startswith("[") and v.endswith("]")):
        try:
            return json.loads(v)
        except Exception:
            return value
    return value

async def get_dynamic_config(force_refresh: bool = False):
    """Fetches dynamic agent configuration from Supabase (Persistent cache)."""
    global _LIVE_CONFIG, _LAST_REFRESH
    now = time.time()
    
    # If we have data and it's fresh enough, just return it.
    if not force_refresh and _LIVE_CONFIG and (now - _LAST_REFRESH) < _CACHE_TTL_SECONDS:
        return _LIVE_CONFIG

    url = f"{settings.SUPABASE_URL}/rest/v1/clinic_settings"
    headers = {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            config = {}
            for item in data:
                config[item["key"]] = _coerce_value(item.get("value"))
            
            _LIVE_CONFIG = config
            _LAST_REFRESH = now
            logger.info("Dynamic settings refreshed in background.")
            return _LIVE_CONFIG
        except Exception as e:
            logger.error(f"Background settings refresh failed: {e}")
            return _LIVE_CONFIG or {}

def get_agent_identity_sync() -> dict:
    """Instant synchronous read of identity from memory."""
    return _LIVE_CONFIG.get('agent_identity', {})

def get_agent_prompt_sync() -> tuple:
    """Instant synchronous read of prompt data from memory."""
    prompt_data = _LIVE_CONFIG.get('agent_prompt', {})
    return prompt_data.get('instructions'), prompt_data.get('greeting')

async def get_agent_snapshot():
    """Fallback async version, but now highly likely to hit RAM cache."""
    config = await get_dynamic_config()
    identity = config.get('agent_identity', {})
    prompt_data = config.get('agent_prompt', {})
    return identity, prompt_data.get('instructions'), prompt_data.get('greeting')

async def start_settings_poller():
    """Background loop to keep settings fresh."""
    while True:
        await get_dynamic_config(force_refresh=True)
        await asyncio.sleep(_CACHE_TTL_SECONDS)
