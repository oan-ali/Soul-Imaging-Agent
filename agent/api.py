"""
api.py - FastAPI server for LiveKit tokens + Admin backend + Orb static file serving.
"""
import os
import uuid
import json
import logging
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from livekit import api
from agent.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-server")

# Directories
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ORB_DIR = os.path.join(_BASE_DIR, "frontend", "Soulbot_Updated", "Frontend")
_ADMIN_DIR = os.path.join(_BASE_DIR, "frontend", "Soulbot_Updated", "Admin", "dist")

app = FastAPI(title="Soulbot API Server")

# Router Fallback for SPA (Single Page Application) - Redirects to safely resolve 404s on refresh
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        path = request.url.path
        # Admin SPA fallback
        if path.startswith("/admin"):
            # If it's a request for a file (has extension), return 404 as normal
            if "." not in path.split("/")[-1]:
                admin_index = os.path.join(_ADMIN_DIR, "index.html")
                if os.path.exists(admin_index):
                    return FileResponse(admin_index)
        
        # Orb fallback (though usually just one page)
        if path.startswith("/orb"):
            if "." not in path.split("/")[-1]:
                orb_index = os.path.join(_ORB_DIR, "index.html")
                if os.path.exists(orb_index):
                    return FileResponse(orb_index)

    return await http_exception_handler(request, exc)

origins = [o.strip() for o in settings.API_ALLOWED_ORIGINS.split(",") if o.strip()]
if origins == ["*"]:
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = origins
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontends (Handled by manual routes above)
if not os.path.isdir(_ORB_DIR):
    logger.warning(f"Orb frontend not found at {_ORB_DIR}")

if not os.path.isdir(_ADMIN_DIR):
    logger.warning(f"Admin distribution not found at {_ADMIN_DIR}. Run 'npm run build' in Admin folder.")

# Supabase Helper
_timeout = httpx.Timeout(10.0, connect=5.0)
_client = httpx.AsyncClient(timeout=_timeout)

async def supabase_request(method: str, endpoint: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None):
    url = f"{settings.SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # Handle UPSERT for POST with on_conflict
    if method == "POST" and params and "on_conflict" in params:
        headers["Prefer"] = "return=representation,resolution=merge-duplicates"
    try:
        if method == "GET":
            response = await _client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await _client.post(url, headers=headers, json=json_data, params=params)
        elif method == "PATCH":
            response = await _client.patch(url, headers=headers, json=json_data, params=params)
        elif method == "DELETE":
            response = await _client.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        if response.text:
            return response.json()
        return None
    except Exception as e:
        error_msg = str(e)
        if 'response' in locals() and hasattr(response, 'text'):
            error_msg += f" | Body: {response.text}"
        logger.error(f"Supabase error ({method} {endpoint}): {error_msg}")
        return None

# API Endpoints

@app.get("/")
async def root_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/orb")

# Serve Frontends
if os.path.isdir(_ORB_DIR):
    app.mount("/orb", StaticFiles(directory=_ORB_DIR, html=True), name="orb")
    logger.info(f"Orb served at /orb")

if os.path.isdir(_ADMIN_DIR):
    app.mount("/admin", StaticFiles(directory=_ADMIN_DIR, html=True), name="admin")
    logger.info(f"Admin Dashboard served at /admin")
else:
    logger.warning(f"Admin distribution not found at {_ADMIN_DIR}. Run 'npm run build' in Admin folder.")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/token")
async def get_token(request: Request):
    try:
        data = await request.json()
        identity = data.get("identity", f"user_{uuid.uuid4().hex[:8]}")
        room_name = data.get("room", f"room_{uuid.uuid4().hex[:8]}")
        token = (
            api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(identity)
            .with_name(identity)
            .with_grants(api.VideoGrants(room_join=True, room=room_name))
            .to_jwt()
        )
        return {"token": token, "room": room_name, "identity": identity, "url": settings.LIVEKIT_URL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")

        # Fetch user from Supabase
        # Check Database
        res = await supabase_request("GET", "team_members", params={"email": f"eq.{email.lower()}"})
        
        if res and len(res) > 0:
            user = res[0]
            if user.get("password") == password:
                return {
                    "status": "success", 
                    "user": {
                        "id": user.get("id"),
                        "name": user.get("name"),
                        "email": user.get("email"),
                        "role": user.get("role")
                    }
                }
        
        # Hardcoded fallback as a fail-safe (e.g., first run before DB seed)
        if email.lower() == "admin@soulimaging.com" and password == "admin123":
            return {
                "status": "success",
                "user": {
                    "id": "admin-001",
                    "name": "Primary Admin",
                    "email": "admin@soulimaging.com",
                    "role": "Super Admin"
                }
            }
            
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/dashboard/stats")
async def get_stats():
    try:
        # Instead of select=count which can be tricky with body/headers, we fetch all ids
        # For a truly production-scale app we'd use a RPC or proper count headers,
        # but for this clinic, fetching the IDs is robust and fast.
        res_all = await supabase_request("GET", "call_logs", params={"select": "call_id,outcome,started_at,duration_seconds"})
        all_calls = res_all if res_all else []
        
        total_calls = len(all_calls)
        
        # Bookings count
        total_bookings = sum(1 for c in all_calls if c.get("outcome") == "booking")
        
        # Monthly calls (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30))
        monthly_calls = 0
        durations = []
        
        for c in all_calls:
            # Monthly count
            started_at_str = c.get("started_at")
            if started_at_str:
                try:
                    # Handle both Z and +00:00 formats
                    dt_str = started_at_str.replace("Z", "+00:00")
                    # Truncate microseconds if they are too long for fromisoformat
                    if "." in dt_str:
                        base, tz = dt_str.split("+")
                        base = base[:26] # Maximum precision for fromisoformat
                        dt_str = f"{base}+{tz}"
                    
                    dt = datetime.fromisoformat(dt_str)
                    if dt.replace(tzinfo=None) > thirty_days_ago:
                        monthly_calls += 1
                except Exception:
                    pass
            
            # Durations for avg
            d = c.get("duration_seconds")
            if d and d > 0:
                durations.append(d)

        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "totalCalls": total_calls,
            "monthlyCalls": monthly_calls,
            "bookings": total_bookings,
            "avgDuration": f"{int(avg_duration // 60)}:{int(avg_duration % 60):02d}",
            "missedCalls": total_calls - total_bookings,
            "successRate": int((total_bookings / total_calls * 100)) if total_calls > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return {"totalCalls": 0, "monthlyCalls": 0, "bookings": 0, "avgDuration": "0:00", "missedCalls": 0, "successRate": 0}

@app.get("/api/calls")
async def get_calls(limit: int = Query(500, ge=1, le=2000)):
    res = await supabase_request(
        "GET",
        "call_logs",
        params={"select": "*", "order": "started_at.desc", "limit": str(limit)},
    )
    return res or []

@app.get("/api/analytics")
async def get_analytics(limit: int = Query(500, ge=1, le=2000)):
    data = await get_calls(limit=limit)
    
    # Target Timezone Offset (Australia/Sydney is UTC+10)
    # Ideally we'd use pytz, but since it's missing we'll use a 10-hour offset
    try:
        offset_hours = 10 if "Sydney" in settings.TIMEZONE else 0
        tz_offset = timedelta(hours=offset_hours)
    except:
        tz_offset = timedelta(hours=0)

    now_utc = datetime.now(timezone.utc)
    now_target = now_utc + tz_offset

    # last 7 days trend
    trend = []
    for i in range(6, -1, -1):
        target_day = (now_target - timedelta(days=i)).date()
        target_day_start = datetime.combine(target_day, datetime.min.time())
        target_day_end = target_day_start + timedelta(days=1)
        
        count = 0
        for c in data:
            started_at_str = c.get("started_at")
            if started_at_str:
                try:
                    dt_utc = datetime.fromisoformat(started_at_str.replace("Z", "+00:00"))
                    dt_target = dt_utc + tz_offset
                    if target_day_start <= dt_target.replace(tzinfo=None) < target_day_end:
                        count += 1
                except:
                    continue
        
        trend.append({"day": target_day.strftime("%a"), "calls": count})

    # outcomes
    outcome_counts: Dict[str, int] = {}
    for c in data:
        key = (c.get("outcome") or "other").lower()
        outcome_counts[key] = outcome_counts.get(key, 0) + 1

    # durations
    buckets = [
        {"range": "0-1m", "min": 0, "max": 60, "count": 0},
        {"range": "1-3m", "min": 60, "max": 180, "count": 0},
        {"range": "3-5m", "min": 180, "max": 300, "count": 0},
        {"range": "5-10m", "min": 300, "max": 600, "count": 0},
        {"range": "10m+", "min": 600, "max": float("inf"), "count": 0},
    ]
    for c in data:
        d = c.get("duration_seconds") or 0
        for b in buckets:
            if b["min"] <= d < b["max"]:
                b["count"] += 1
                break

    return {"trend": trend, "outcomes": outcome_counts, "durations": [{"range": b["range"], "count": b["count"]} for b in buckets]}

@app.get("/api/dashboard/notifications")
async def get_notifications():
    try:
        res = await supabase_request("GET", "call_logs", params={"select": "call_id,outcome,started_at", "limit": "20", "order": "started_at.desc"})
        notifications = []
        for c in (res or []):
            o = (c.get("outcome") or "").lower()
            if o == "booking":
                notifications.append({
                    "id": c["call_id"],
                    "type": "booking",
                    "title": "New Booking",
                    "message": "A new appointment was scheduled successfully.",
                    "time": c["started_at"]
                })
            elif o == "callback":
                notifications.append({
                    "id": c["call_id"],
                    "type": "callback",
                    "title": "Callback Request",
                    "message": "A caller requested a follow-up call.",
                    "time": c["started_at"]
                })
        return notifications[:5]
    except Exception:
        return []

@app.get("/api/agent/config")
async def get_config():
    res = await supabase_request("GET", "clinic_settings")
    if not res:
        return {}
    config: Dict[str, Any] = {}
    for item in res:
        val = item.get("value")
        if isinstance(val, str):
            v = val.strip()
            if (v.startswith("{") and v.endswith("}")) or (v.startswith("[") and v.endswith("]")):
                try:
                    val = json.loads(v)
                except Exception:
                    pass
        config[item["key"]] = val
    return config

@app.post("/api/agent/config")
async def update_config(request: Request):
    data = await request.json()
    try:
        rows: List[Dict[str, Any]] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            rows.append({"key": key, "value": value, "updated_at": datetime.now().isoformat()})

        res = await supabase_request(
            "POST",
            "clinic_settings",
            json_data=rows,
            params={"on_conflict": "key"},
        )
        if res is None:
            raise HTTPException(status_code=500, detail="Database update failed")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge")
async def get_knowledge():
    base_dir = os.path.dirname(__file__)
    data_dirs = [
        os.path.join(base_dir, "knowledge", "data"),
        os.path.join(base_dir, "knowledge", "docs")
    ]

    files = []
    for d in data_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith((".json", ".pdf", ".docx", ".txt", ".md")):
                    files.append({"id": f, "name": f, "type": "file", "status": "indexed"})
    return files


@app.post("/api/knowledge/sync")
async def sync_knowledge(background_tasks: BackgroundTasks):
    from agent.knowledge.loader import ingest_knowledge_base
    background_tasks.add_task(ingest_knowledge_base)
    return {"status": "processing"}

@app.get("/api/team")
async def get_team():
    # Only return public fields, exclude password for security
    res = await supabase_request("GET", "team_members", params={"select": "id,name,role,email,status,created_at"})
    return res or []

@app.post("/api/team")
async def add_team_member(request: Request):
    data = await request.json()
    try:
        # Generate a unique ID if not provided
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        
        # Set a default password if none was provided
        if not data.get("password"):
            data["password"] = "soulbot123"
        
        res = await supabase_request(
            "POST", 
            "team_members", 
            json_data=data,
            params={"on_conflict": "email"}
        )
        if res is None:
            raise HTTPException(
                status_code=500, 
                detail="Failed to add team member. Ensure the 'password' column exists in your Supabase 'team_members' table (run supabase_schema.sql)."
            )
        return {"status": "success", "member": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/team/{member_id}")
async def delete_team_member(member_id: str):
    try:
        await supabase_request(
            "DELETE",
            "team_members",
            params={"id": f"eq.{member_id}"}
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
