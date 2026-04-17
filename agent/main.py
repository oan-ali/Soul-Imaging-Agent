"""
main.py - Flawless & Concurrency-Safe LiveKit Agent Worker.
"""
import logging
import asyncio

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    voice,
    AgentSession,
)

from agent.voice_pipeline import get_stt, get_llm, get_tts, get_vad
from agent.knowledge.loader import ingest_knowledge_base
from agent.call.lifecycle import CallLifecycleManager
from agent.prompt import build_system_prompt
from agent.tools import get_all_tools
from agent.config import settings
from agent.settings import get_agent_identity_sync, get_agent_prompt_sync, start_settings_poller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("soulbot-worker")

async def prewarm(proc):
    """Pre-load heavy assets during worker boot."""
    proc.userdata["vad"] = get_vad()
    logger.info("VAD Model Pre-loaded.")
    
    # Fire off heavy background tasks
    asyncio.create_task(ingest_knowledge_base())
    asyncio.create_task(start_settings_poller())
    logger.info("Background pre-warming (KB + Config Poller) started.")

async def entrypoint(ctx: JobContext):
    """Restored entrypoint using Agent + AgentSession with improved reliability."""
    logger.info(f"Connecting to room: {ctx.room.name}")
    
    # 1. Connect immediately
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # 2. Get Settings
    identity = get_agent_identity_sync()
    instructions, greeting = get_agent_prompt_sync()
    lifecycle = CallLifecycleManager(ctx.room.name)

    # 3. Initialize Agent
    # We use voice.Agent as required by this environment's libraries
    agent = voice.Agent(
        stt=get_stt(),
        llm=get_llm(),
        tts=get_tts(),
        vad=get_vad(),
        instructions=instructions or build_system_prompt(),
        tools=get_all_tools(lifecycle),
        min_endpointing_delay=0.5,
        max_endpointing_delay=1.0,
    )

    # 4. Initialize Session
    session = AgentSession(
        user_away_timeout=15.0,
        aec_warmup_duration=0.1,
        preemptive_generation=True,
    )

    # 5. Start
    await session.start(agent, room=ctx.room)
    logger.info(f"Session established for {identity.get('name', 'Sarah')}")

    # 6. Greeting
    final_greeting = greeting or f"Hello, I am {settings.AGENT_NAME} from {settings.CLINIC_NAME}. How can I help you today?"
    await session.say(final_greeting, allow_interruptions=True)

    # 7. Stable Wait Condition
    # We use a standard asyncio Event to keep the process alive
    # wait_until_disconnected() was not found in this SDK version
    stop_event = asyncio.Event()
    
    @ctx.add_shutdown_callback
    def _on_job_shutdown():
        stop_event.set()

    logger.info("Agent session active. Sarah is waiting for your input...")
    await stop_event.wait()

    # 8. Shutdown and Cleanup
    @ctx.add_shutdown_callback
    async def on_shutdown():
        logger.info("Call lifecycle finalizing...")
        transcript = []
        try:
            # Safely extract messages from ChatContext
            # Try items attribute first (Agent style), then messages() method
            messages = []
            if hasattr(agent.chat_ctx, "messages"):
                messages = agent.chat_ctx.messages() if callable(agent.chat_ctx.messages) else agent.chat_ctx.messages
            elif hasattr(agent.chat_ctx, "items"):
                messages = agent.chat_ctx.items

            for item in messages:
                role = getattr(item, "role", None)
                if role in ("user", "assistant"):
                    # Content can be a string or a list of parts
                    content = getattr(item, "content", "")
                    transcript.append({"role": role, "content": str(content)})
        except Exception as e:
             logger.error(f"Error building transcript history: {e}")

        await lifecycle.finalize(transcript)
        logger.info("Call lifecycle finalized.")





if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
